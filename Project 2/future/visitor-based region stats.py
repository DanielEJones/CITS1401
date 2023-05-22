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


class RegionStatCalculator:

    def visit(self, country: Country) -> None:
        ...

    def calculate(self) -> any:
        ...


class Region:
    _name: str
    _land_area: int
    _population: int
    _countries: list[Country]

    def __init__(self, name: str) -> None:
        self._name = name
        self._land_area, self._population = 0, 0
        self._countries = []

    def append(self, country: Country) -> None:
        self._land_area += country.land_area
        self._population += country.population
        self._countries.append(country)

    @property
    def land_area(self):
        return self._land_area

    @property
    def population(self):
        return self._population

    @property
    def number_of_countries(self):
        return len(self._countries)

    def calculate(self, *functions: type[RegionStatCalculator]):
        funcs: tuple[RegionStatCalculator] = tuple(func() for func in functions)
        for country in self._countries:
            for func in funcs:
                func.visit(country)
        return tuple(func.calculate() for func in funcs) if len(funcs) > 1 else funcs[0].calculate()


class PopulationStandardError(RegionStatCalculator):

    def __init__(self):
        self._length, self._total_pop = 0, 0
        self._populations = []

    def visit(self, country: Country) -> None:
        self._populations.append(country.population)
        self._total_pop += country.population
        self._length += 1

    def calculate(self) -> float:
        mean = self._total_pop / self._length
        mean_differences = (population - mean for population in self._populations)
        standard_deviation = sum(x ** 2 for x in mean_differences) / (self._length - 1)
        return (standard_deviation / self._length) ** 0.5


class PopulationAreaSimilarity(RegionStatCalculator):

    def __init__(self):
        self._land_population_product, self._land_squared, self._population_squared = 0, 0, 0

    def visit(self, country: Country) -> None:
        self._land_squared += country.land_area * country.land_area
        self._population_squared += country.population * country.population
        self._land_population_product += country.land_area * country.population

    def calculate(self) -> float:
        return self._land_population_product / (self._population_squared * self._land_squared) ** 0.5


class CountryDictionary(RegionStatCalculator):

    def __init__(self):
        self._countries = []
        self._total_pop = 0

    def visit(self, country: Country) -> None:
        self._countries.append(country)
        self._total_pop += country.population

    def calculate(self) -> dict[str, list[int, int, float, float, int]]:
        countries = sorted(self._countries, key=Country.rank)
        return {
            country.name:
            [country.population, country.net_change, (country.population / self._total_pop) * 100, country.density, pos]
            for pos, country in enumerate(countries, 1)
        }


if __name__ == '__main__':
    r = Region('Europe')
    r.append(Country('Britain', 'Europe', 100, 100, 0))
    r.append(Country('Norway', 'Europe', 50, 99, 0))
    sim, error, dic = r.calculate(PopulationAreaSimilarity, PopulationStandardError, CountryDictionary)
    print(f'{[sim, error]}\n{dic}')
