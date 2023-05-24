class Country:
    """Representation of a Country. Has a name, region, population, land area, and a change in population."""

    # A country has the following attributes. Underscore suggests that they are not to be accessed from outside instance
    _name: str
    _region: str
    _land_area: int
    _population: int
    _net_change: int

    def __init__(self, name: str, region: str, land_area: int, population: int, net_change: int) -> None:
        self._name, self._region, self._land_area, self._population, self._net_change = \
            name, region, land_area, population, net_change

    # The property decorator means that the attributes can be accessed as country.name rather than .name()
    # It also means that these properties are read only, ensuring that the country is not changed after creation.
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
        """Method to be used in sorted() as a key to sort a list of countries by population, density and name."""
        return -self.population, -self.density, self.name


class RegionStatCalculator:
    """Abstract representation of something that would calculate statistics for a region."""

    def visit(self, country: Country) -> None:
        """Visits a country, gathering necessary data."""

    def calculate(self) -> any:
        """Performs calculations on the gathered data and returns an output."""


class PopulationStandardError(RegionStatCalculator):
    """Calculates the Standard Error of Country populations in a region."""

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
    """Calculates the Cosine Similarity between the area and population of countries within a region."""

    def __init__(self) -> None:
        self._land_population_product, self._land_squared, self._population_squared = 0, 0, 0

    def visit(self, country: Country) -> None:
        self._land_squared += country.land_area * country.land_area
        self._population_squared += country.population * country.population
        self._land_population_product += country.land_area * country.population

    def calculate(self) -> float:
        return self._land_population_product / (self._population_squared * self._land_squared) ** 0.5


class CountryDictionary(RegionStatCalculator):
    """
    Constructs a representation of the region in the form of a dictionary:
        {Country Name: [population, net change, percentage of region's population, density, rank within region], ...}
    """

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


class Region:
    """Representation of a region. Has a name, a total area, a total population, and a list of countries."""

    _name: str
    _land_area: int
    _population: int
    _countries: list[Country]

    def __init__(self, name: str) -> None:
        self._name = name
        self._land_area, self._population = 0, 0
        self._countries = []

    def append(self, country: Country) -> None:
        """Adds a Country to the region."""

        self._countries.append(country)

        # Add the Country's data to the total.
        self._land_area += country.land_area
        self._population += country.population

    @property
    def name(self) -> str:
        return self._name.lower()

    @property
    def land_area(self) -> int:
        return self._land_area

    @property
    def population(self) -> int:
        return self._population

    @property
    def countries(self) -> list[Country]:
        # Return a copy of the list, so that external use doesn't impact internal representation.
        # Countries are read-only, so I haven't bothered copying them to prevent tampering.
        return [item for item in self._countries]

    @property
    def number_of_countries(self) -> int:
        return len(self._countries)

    def calculate(self, *functions: type[RegionStatCalculator]) -> tuple:
        """Method that takes any number of RegionStatCalculators and returns their outputs."""

        # Constructs the objects passed in to the method and stores them within a tuple
        funcs: tuple[RegionStatCalculator] = tuple(func() for func in functions)

        # Loop through each country in the region and pass it to each CountryStatCalculator object
        for country in self._countries:
            for func in funcs:
                func.visit(country)

        # Call .calculate() on each CountryStatCalculator object and store the output in a tuple. If there is only one
        # CountryStatCalculator, simply return the output (not in a tuple)
        return tuple(func.calculate() for func in funcs) if len(funcs) > 1 else funcs[0].calculate()


class Header:
    """Representation of a Header in a CSV file. Has a name, an index, and a method to validate an item."""

    _name: str
    _index: int
    _type: [str, int, float, bool]
    _validator: [callable, None]

    def __init__(self, name: str, index: int, type_, validator=None) -> None:
        self._name, self._index, self._type, self._validator = name, index, type_, validator

    @property
    def name(self) -> str:
        return self._name.lower()

    @property
    def index(self) -> int:
        return self._index

    def validate(self, data: any) -> bool:
        """Checks whether an item fits the specified type and passes a given validation statement."""
        return isinstance(data, self._type) and (self._validator(data) if self._validator is not None else True)


class DataStream:
    """Abstract representation of an iterable that can peek the next item and skip an item."""

    def peek(self) -> str:
        """Peeks the next item in the stream."""

    def skip(self) -> None:
        """Skips an item."""

    def __iter__(self):
        ...

    def __next__(self):
        ...


class BufferedStream(DataStream):
    """Data stream that reads data in chunks to prevent accessing a file too many times."""

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

        # If the buffer remains empty after filling, the file is empty, so terminate the loop.
        if self._buffer_is_empty():
            raise StopIteration

        # Gets the first item from the buffer, returns it, and removes it from the buffer.
        char = self._buffer.pop(0)
        return char

    def _remaining(self) -> int:
        return len(self._buffer)

    def _buffer_is_empty(self) -> bool:
        return self._remaining() < 1

    def _fill_buffer(self) -> None:
        self._buffer = [char for char in self._file.read(self._buffer_size)]

    def peek(self) -> str:
        """Returns the next item in the buffer without removing it."""

        # Since we remove items from the buffer as they are called upon, the next item in the buffer is also the first.
        # Therefore, we need to check that the buffer is not empty, and fill it if it is.
        if self._buffer_is_empty():
            self._fill_buffer()

        # Return the next character if it exists, else Null
        return self._buffer[0] if not self._buffer_is_empty() else '\0'

    def skip(self) -> None:
        """Skips the next character in the file."""
        self._buffer = self._buffer[1:]


class CSVReader:
    """Class that takes a CSV-Formatted File in the form of a Data Stream and yields a list of items for each row."""

    def __init__(self, file: DataStream, headers=False, escape='\"', delimiter=',', linebreak='\n') -> None:
        self._file = file
        self._escape, self._delimiter, self._linebreak = escape, delimiter, linebreak

        # Store the headers (the first line in the file) if required
        self.headers = self.__next__() if headers else None

    def __iter__(self) -> object:
        return self

    def __next__(self) -> list[str]:
        is_escaped, string, row = False, [], []
        for character in self._file:
            # If we encounter an escape character, and the next character is also an escape character, append it and
            # skip the next character.
            if self._escape in character and self._escape in self._file.peek():
                self._file.skip()
                string.append(character)
                continue

            # If we encounter an escape character that is not escaping an upcoming escape character, take note of it but
            # do not append.
            if self._escape in character:
                is_escaped = not is_escaped
                continue

            # If we encounter the delimiter and are not escaped, add the current string to the row, but don't append
            # the delimiter.
            if self._delimiter in character and not is_escaped:
                row.append(''.join(item for item in string))
                string = []
                continue

            # If the current character is a linebreak, append the current character and return the row, breaking the
            # loop until the next call of __next__()
            if self._linebreak in character and not is_escaped:
                row.append(''.join(item for item in string))
                return row

            # If the character is nothing special, append it and move on
            string.append(character)

        # If the file is exhausted, but we still have data stored, append it to the row and return the current row.
        if string:
            row.append(''.join(item for item in string))
            return row

        raise StopIteration


def round_output(places: int):
    """Decorator function that rounds the output of a function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            def round_through(items) -> [tuple, list, dict]:

                def round_(float_) -> [float, any]:
                    return round(float_, places) if isinstance(float_, float) else float_

                def is_list(item) -> bool:
                    return type(item) in (list, tuple, dict)

                def round_list(data) -> [list, tuple]:
                    return type_(round_(item) if not is_list(item) else round_through(item) for item in data)

                def round_dict(dic) -> dict:
                    return {key: round_(val) if not is_list(val) else round_through(val) for key, val in dic.items()}

                type_ = type(items)
                return round_list(items) if type_ in (list, tuple) \
                    else round_dict(items) if isinstance(items, dict) \
                    else round_(items)

            func_out = func(*args, **kwargs)
            return round_through(func_out)
        return wrapper
    return decorator


@round_output(places=4)
def main():
    ...
