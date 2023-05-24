def round_output(places: int):
    def decorator(func):
        def wrapper(*args, **kwargs):
            def round_through(items):

                def round_(float_):
                    return round(float_, places) if isinstance(float_, float) else float_

                def is_list(item):
                    return type(item) in (list, tuple, dict)

                def round_list(data):
                    return type_(round_(item) if not is_list(item) else round_through(item) for item in data)

                def round_dict(dic):
                    return {key: round_(val) if not is_list(val) else round_through(val) for key, val in dic.items()}

                type_ = type(items)
                return round_list(items) if type_ in (list, tuple) else round_dict(items)

            func_out = func(*args, **kwargs)
            return round_through(func_out)
        return wrapper
    return decorator


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
    def land_area(self) -> int:
        return self._land_area

    @property
    def population(self) -> int:
        return self._population

    @property
    def number_of_countries(self) -> int:
        return len(self._countries)

    def calculate(self, *functions: type[RegionStatCalculator]) -> any:
        funcs: tuple[RegionStatCalculator] = tuple(func() for func in functions)
        for country in self._countries:
            for func in funcs:
                func.visit(country)
        return tuple(func.calculate() for func in funcs) if len(funcs) > 1 else funcs[0].calculate()


class PopulationStandardError(RegionStatCalculator):

    def __init__(self) -> None:
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

    def __init__(self) -> None:
        self._land_population_product, self._land_squared, self._population_squared = 0, 0, 0

    def visit(self, country: Country) -> None:
        self._land_squared += country.land_area * country.land_area
        self._population_squared += country.population * country.population
        self._land_population_product += country.land_area * country.population

    def calculate(self) -> float:
        return self._land_population_product / (self._population_squared * self._land_squared) ** 0.5


class CountryDictionary(RegionStatCalculator):

    def __init__(self) -> None:
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


@round_output(places=4)
def main(*funcs):
    r = Region('Europe')
    r.append(Country('Germany', 'Europe', 348_560, 83_783_942, 266_897))
    r.append(Country('United Kingdom', 'Europe', 241_930, 67_886_011, 355_839))
    r.append(Country('Norway', 'Europe', 365_268, 5_421_241, 42_384))
    r.append(Country('Spain', 'Europe', 498_800, 46_754_778, 18_002))
    r.append(Country('France', 'Europe', 547_557, 65_273_511, 143_783))
    r.append(Country('Russia', 'Europe', 16_376_870, 145_934_462, 62_206))
    r.append(Country('Italy', 'Europe', 294_140, 60_461_826, -88_249))
    return r.calculate(*funcs)


if __name__ == '__main__':
    sim, err, diction = main(PopulationAreaSimilarity, PopulationStandardError, CountryDictionary)
    print([sim, err])
    print(diction)
