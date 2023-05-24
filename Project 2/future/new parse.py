class InsensitiveString(str):

    def __eq__(self, other):
        return self.casefold() == other.casefold()


class Country:

    _name: str
    _region: str
    _land_area: int
    _population: int
    _net_change: int

    def __init__(self, name: str, region: str, land_area: int, population: int, net_change: int) -> None:
        self._name, self._region, self._land_area, self._population, self._net_change = name, region, land_area, population, net_change

    @property
    def name(self) -> str:
        return self._name.lower()

    @property
    def region(self) -> str:
        return self._region.lower()

    @property
    def land_area(self) -> int:
        return self._land_area

    @property
    def population(self) -> int:
        return self._population

    @property
    def net_change(self) -> int:
        return self._net_change

    @property
    def density(self) -> float:
        return self.population / self.land_area

    def rank(self) -> tuple[int, float, str]:
        return -self.population, -self.population / self.land_area, self.name


class RegionStatsCalculator:

    def visit(self, country: Country) -> None:
        """Performs some action on country data."""

    def calculate(self) -> any:
        """Performs some action on gathered data and returns an output."""


class PopulationStandardError(RegionStatsCalculator):

    def __init__(self) -> None:
        self._length, self._total_pop = 0, 0
        self._populations = []

    def visit(self, country: Country) -> None:
        self._populations.append(country.population)
        self._total_pop += country.population
        self._length += 1

    def calculate(self) -> float:
        mean = self._total_pop / self._length
        mean_difference = (x - mean for x in self._populations)
        variance = sum(x ** 2 for x in mean_difference) / (self._length - 1)
        return (variance / self._length) ** 0.5


class PopulationAreaSimilarity(RegionStatsCalculator):

    def __init__(self) -> None:
        self._land_population_product, self._land_squared, self._population_squared = 0, 0, 0

    def visit(self, country: Country) -> None:
        self._land_squared += country.land_area * country.land_area
        self._population_squared += country.population * country.population
        self._land_population_product += country.land_area * country.population

    def calculate(self) -> float:
        return self._land_population_product / (self._population_squared * self._land_squared) ** 0.5


class Region:

    _name: str
    _land_area: int
    _population: int
    _countries: list[Country]

    def __init__(self, name: str) -> None:
        self._name = name
        self._population, self._land_area = 0, 0
        self._countries = []

    def append(self, country: Country) -> None:
        self._land_area += country.land_area
        self._population += country.population
        self._countries.append(country)

    def calculate(self, function: type[RegionStatsCalculator]):
        func = function()
        for country in self._countries:
            func.visit(country)
        return func.calculate()

    @property
    def name(self) -> str:
        return self._name.lower()

    @property
    def population(self, update: bool = False) -> int:
        return self._population if not update else sum(country.population for country in self._countries)

    @property
    def land_area(self, update: bool = False) -> int:
        return self._land_area if not update else sum(country.land_area for country in self._countries)

    @property
    def num_countries(self) -> int:
        return len(self._countries)

    @property
    def countries(self) -> dict[str, list[int, int, float, int]]:
        countries = sorted(self._countries, key=Country.rank)
        return {country.name: [country.population, country.net_change, (country.population / self.population) * 100, country.density, pos] for pos, country in enumerate(countries, 1)}


class Header:

    _name: str
    _index: int
    _type: [str, int, float, bool]
    _validator: [callable, None]

    def __init__(self, name: str, index: int, type_, validator=None) -> None:
        self._name, self._index, self._type, self._validator = name, index, type_, validator

    def __repr__(self):
        return f'Header({self.name}, {self.index})'

    @property
    def name(self) -> str:
        return self._name.lower()

    @property
    def index(self) -> int:
        return self._index

    def validate(self, data: any) -> bool:
        return isinstance(data, self._type) and (self._validator(data) if self._validator is not None else True)


class DataStream:

    def current(self) -> str:
        ...

    def peek(self) -> str:
        ...

    def __iter__(self):
        ...

    def __next__(self):
        ...


class BufferedStream(DataStream):

    _buffer: list
    _buffer_size: int

    def __init__(self, file, size: int) -> None:
        if size < 1:
            raise ValueError(f'Buffer Size must be greater than 0. Got {size} instead.')
        self._file = file
        self._buffer_size = size
        self._buffer = []

    def __iter__(self):
        return self

    def __next__(self):
        if self._buffer_is_empty():
            self._fill_buffer()
        char = self._buffer[0]
        self._buffer = self._buffer[1:]
        return char

    def _fill_buffer(self) -> None:
        self._buffer = [char for char in self._file.read(self._buffer_size)]
        if self._buffer_is_empty():
            raise StopIteration

    def _remaining(self) -> int:
        return len(self._buffer)

    def _buffer_is_empty(self) -> bool:
        return self._remaining() < 1

    def peek(self) -> str:
        if self._remaining() == 0:
            self._fill_buffer()
            return self._buffer[0]
        if self._remaining() <= 1:
            self._file.seek(self._file.tell() - 1)
            self._fill_buffer()
        return self._buffer[1] if self._remaining() > 1 else '\0'


class CSVReader:

    def __init__(self, file: DataStream, headers=False, escape='\"', delimiter=',', linebreak='\n') -> None:
        self._file = file
        self._escape, self._delimiter, self._linebreak = escape, delimiter, linebreak
        self.headers = self.__next__() if headers else None

    def __iter__(self) -> object:
        return self

    def __next__(self) -> list[str]:
        is_escaped, string, row = False, [], []
        for character in self._file:
            if self._escape in character:
                is_escaped = not is_escaped
                continue
            if self._delimiter in character and not is_escaped:
                row.append(''.join(item for item in string))
                string = []
                continue
            if self._linebreak in character and not is_escaped:
                row.append(''.join(item for item in string))
                return row
            string.append(character)
        if string:
            row.append(''.join(item for item in string))
            return row
        raise StopIteration


class CSVCountryHandler:

    _headers: list[Header]
    _regions: dict[str, Region]

    def __init__(self) -> None:
        self._headers = []
        self._regions = {}

    def _extract_row_data(self, row) -> tuple:
        extracted = []
        for header in self._headers:
            item = set_type(row[header.index])
            if not header.validate(item):
                raise ValueError(f'Bad Types: ({header.name}: {item}), was expecting {header._type}')
            extracted.append(item)
        return tuple(extracted)

    def on_header(self, headers_received: list, *expected_headers: tuple):
        headers_received = tuple(InsensitiveString(item) for item in headers_received)
        for header in expected_headers:
            name, type_, *valid = header
            if name not in headers_received:
                raise ValueError(f'Header missing: {name}.')
            h = Header(name, headers_received.index(name), type_, valid[0] if valid else None)
            self._headers.append(h)

    def on_row(self, data: list) -> None:
        extract = self._extract_row_data(data)
        new_country = Country(*extract)
        if new_country.region not in self._regions:
            self._regions[new_country.region] = Region(new_country.region)
        self._regions[new_country.region].append(new_country)

    def on_finish(self) -> [dict, dict]:
        stats, regions = {}, {}
        for region in self._regions.values():
            stats[region.name] = [region.calculate(PopulationStandardError), region.calculate(PopulationAreaSimilarity)]
            regions[region.name] = region.countries
        return stats, regions


def set_type(item):
    return int(item) if item.lstrip('-+').isdigit() else item


def main():

    with open('../Countries.csv', 'r') as csv_file:
        csv_file = BufferedStream(csv_file, 10)
        reader = CSVReader(csv_file, headers=True)
        handler = CSVCountryHandler()
        headers = [('Country', str), ('Regions', str), ('Land Area', int, lambda v: v >= 0), ('Population', int, lambda v: v >= 0), ('Net Change', int)]
        handler.on_header(reader.headers, *headers)
        for row in reader:
            handler.on_row(row)
        return handler.on_finish()


if __name__ == '__main__':
    o1, o2 = main()
    print(o2)
