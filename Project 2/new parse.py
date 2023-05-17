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


class CSVReader:

    def __init__(self, file, headers=False, escape='\"', delimiter=',', linebreak='\n'):
        self._file = (character for character in file)
        self._escape, self._delimiter, self._linebreak = escape, delimiter, linebreak
        self.headers = self.__next__() if headers else None

    def __iter__(self):
        return self

    def __next__(self):
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


def row_is_valid(row: list, headers: list[Header]) -> bool:
    return all(header.validate(row[header.index]) for header in headers)


def construct_headers(names: tuple, types: tuple, validations: tuple, headers) -> list:
    h = []
    for name, type, validation in zip(names, types, validations):
        index = headers.index(name)
        h.append(Header(name, index, type, validation))
    return h


if __name__ == '__main__':
    c = CSVReader('hello,world\npart,deux', headers=True)
    hh = construct_headers(names=('hello', 'world'), types=(str, str), validations=(None, None), headers=c.headers)
    print(hh)
        
