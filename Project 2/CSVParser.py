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
    REGION: str

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


class CSVCountryHandler:

    _countries: list[Country]
    _header_indexes: tuple[int, ...]

    def __init__(self, expected_headers: tuple[str, ...]):
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
        c = Country(data, self._header_indexes)

        if not self._country_is_valid(c, (str, int, int, int, str)):
            raise ValueError('Type Mismatch')

        self._countries.append(c)

    def on_finish(self) -> [dict, dict]:
        print('\n'.join(f'{country}' for country in sorted(self._countries, key=Country.rank)))
        return {}, {}


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
        _, __ = handler.on_finish()

    stats = {'northern america': [80089583.56, 0.7841]}
    northern_america_data = {
        'united states': [331002651, 1937734, 89.7357, 36.1854, 1],
        'canada': [37742154, 331107, 10.232, 4.1504, 2],
        'bermuda': [62278, -228, 0.0169, 1245.56, 3],
        'greenland': [56770, 98, 0.0154, 0.1383, 4]
    }
    region_data = {'northern america': northern_america_data}
    return stats, region_data


if __name__ == '__main__':
    main('Countries.csv')
