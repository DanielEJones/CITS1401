class CSVReader:

    def __init__(self, file, headers=False, escape='\"', delimiter=',', linebreak='\n'):
        self._file = (character for character in file)
        self._escape, self._delimiter, self._linebreak = escape, delimiter, linebreak
        self.headers = self.__next__() if headers else None

    def __iter__(self):
        return self

    def __next__(self) -> list[str]:
        escaped, string, row = False, [], []
        for character in self._file:
            if self._escape in character:
                escaped = not escaped
                continue
            if self._delimiter in character and not escaped:
                row.append(''.join(item for item in string))
                string = []
                continue
            if self._linebreak in character and not escaped:
                row.append(''.join(item for item in string))
                return row
            string.append(character)
        if string:
            row.append(''.join(item for item in string))
            return row
        raise StopIteration


class Country:

    NAME: str
    POPULATION: int
    NET_CHANGE: int
    LAND_AREA: int

    def __init__(self, data: list[str], headers: tuple[int, ...]):
        self.NAME, self.POPULATION, self.NET_CHANGE, self.LAND_AREA, self.REGION = (data[i] for i in headers)
        self._data = (self.NAME, self.POPULATION, self.NET_CHANGE, self.LAND_AREA, self.REGION)

    def __repr__(self):
        return f'{self.NAME}=({self.POPULATION=:.3f}, {self.LAND_AREA=}, {self.REGION=})'

    def rank(self):
        return -self.POPULATION, -self.POPULATION / self.LAND_AREA, self.NAME

    @property
    def data(self):
        return self._data


class Region:

    NAME: str
    COUNTRIES: list[Country]

    def __init__(self, name: str):
        self.NAME = name
        self.COUNTRIES = []

    def __repr__(self):
        return f'{self.COUNTRIES}'

    def append(self, country: Country):
        self.COUNTRIES.append(country)

    @property
    def population(self) -> int:
        return sum(country.POPULATION for country in self.COUNTRIES)

    @property
    def land_area(self) -> int:
        return sum(country.LAND_AREA for country in self.COUNTRIES)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    return sum(an * bn for an, bn in zip(a, b)) / (sum(an ** 2 for an in a) * sum(bn ** 2 for bn in b)) ** 0.5


def standard_error(mean: float, items: list[float]) -> float:
    result = (sum((x - mean) ** 2 for x in items) / (len(items) - 1)) ** 0.5
    return result / len(items) ** 0.5


class CSVCountryHandler:

    _regions: dict[str: Region]
    _countries: list[Country]
    _header_indexes: tuple[int, ...]

    def __init__(self, expected_headers: tuple[str, ...]):
        self._regions = {}
        self._countries = []
        self._headers = expected_headers

    @staticmethod
    def _type_data(item: str) -> [int, str]:
        return int(item) if item.lstrip('-+').isdigit() else item

    @staticmethod
    def _country_is_valid(country: Country, expected_types: tuple) -> bool:
        return tuple(type(item) for item in country.data) == expected_types

    def on_header(self, received: list[str]) -> None:
        received = tuple(heading.lower() for heading in received)
        try:
            self._header_indexes = tuple(received.index(header) for header in self._headers)
        except ValueError:
            raise ValueError('At least one header missing.')

    def on_row(self, data: list[str]) -> None:

        if not hasattr(self, '_header_indexes'):
            raise AttributeError('No Headers')

        if any(item in {None, '\0', ''} for item in data):
            raise ValueError('Row contains missing data')

        data = [self._type_data(item) for item in data]
        new_country = Country(data, self._header_indexes)

        if not self._country_is_valid(new_country, (str, int, int, int, str)):
            raise ValueError('Type Mismatch')

        if new_country.REGION not in self._regions:
            self._regions[new_country.REGION] = Region(new_country.REGION)
        self._regions[new_country.REGION].append(new_country)

    def on_finish(self) -> [dict, dict]:
        regions, stats = {}, {}
        for region in self._regions.values():

            countries = sorted(region.COUNTRIES, key=Country.rank)
            region_data = {}
            land, pop = [], []

            for pos, country in enumerate(countries, 1):

                land.append(country.LAND_AREA)
                pop.append(country.POPULATION)
                region_data[country.NAME] = [country.POPULATION, country.NET_CHANGE, (country.POPULATION / region.population) * 100, (country.POPULATION / country.LAND_AREA), pos]

            mean = sum(pop) / len(pop)
            stats[region.NAME] = [standard_error(mean, pop), cosine_similarity(land, pop)]
            regions[region.NAME] = region_data
        return stats, regions


# Covered by on_header() method in "CSVCountryHandler
def get_header_indexes(received: list[str], expected: tuple[str, ...]) -> tuple[int, ...]:
    received = tuple(heading.lower() for heading in received)
    return tuple(received.index(header) for header in expected)


# Covered by _type_data() method in "CSVCountryHandler"
def set_type(item: str) -> [str, int]:
    return int(item) if item.lstrip('-+').isdigit() else item


def main(file):

    with open(file, 'r') as csv_file:
        reader = CSVReader(csv_file.read(), headers=True)
        handler = CSVCountryHandler(expected_headers=('country', 'population', 'net change', 'land area', 'regions'))
        handler.on_header(reader.headers)
        for country in reader:
            handler.on_row(country)
        o1, o2 = handler.on_finish()

    return o1, o2


if __name__ == '__main__':
    m, n = main('Countries.csv')
    print(n['Europe'])

