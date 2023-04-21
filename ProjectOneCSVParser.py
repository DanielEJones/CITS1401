# Author: Daniel Jones, SN 23821639

class BufferedReader:

    def __init__(self, file, size: int) -> None:
        # If there is no Buffer, raise an exception
        if size < 1:
            raise ValueError('Buffer size must be greater than or equal to 1')
        self.file = file
        self.file.seek(0)
        self.buffer_size = size
        self.buffer = self.fill_buffer(self.buffer_size)

        # index set to minus 1 so that the first call of __next__ or .peek() returns self.buffer[0]
        self.index = -1

    def __iter__(self) -> object:
        return self

    def __next__(self) -> str:
        # get the next character
        self.traverse(1)
        try:
            return self.current()
        except IndexError:
            # if the current character does not exist, stop iterating
            raise StopIteration

    def fill_buffer(self, size) -> str:
        # read the number of characters equal to size plus one, and reset the index
        self.index = 0
        return self.file.read(size + 1)

    def traverse(self, k) -> None:
        self.index += k
        # If the new index exceeds the Buffer, refill the buffer starting from the new index:
        if self.index > self.buffer_size:
            self.file.seek(self.file.tell() + (self.index - self.buffer_size) - 1)
            self.buffer = self.fill_buffer(self.buffer_size)

    def current(self) -> str:
        return self.buffer[self.index] if self.index > 0 else self.buffer[0]

    def peek(self) -> str:
        try:
            # attempt to return the next item in buffer
            char = self.buffer[self.index + 1]
        except IndexError:
            try:
                # if the next character is outside the buffer, fill the buffer from the current character onward
                self.file.seek(self.file.tell() - 1)
                self.buffer = self.fill_buffer(self.buffer_size)
                # attempt to return next item in buffer
                char = self.buffer[self.index + 1]
            except IndexError:
                # if we fail again, the next character does not exist and so return null
                char = '\0'
        return char


def csv_read(file, split=',', linebreak='\n', escape='\"') -> list:
    """Generator Function that yields the lines of a CSV file as a list, one line at a time"""

    # The Buffer size is simply a sufficiently large number
    # Any value would work, but larger ones reduce the times the file has to be accessed and is hence faster
    file = BufferedReader(file, 1000)

    # Initialise variables
    string = ''
    row = []
    escaped = False

    # for each character in file:
    for character in file:

        # skip double quotes, make note that we have seen double quotes, then continue
        if escape in character:
            # if the next character is a double quote also, then rather than escaping the line we append a double quote
            if escape in file.peek():
                # skip the next character, so as not to prematurely close the escape
                # however we don't continue, so that character is still appended
                file.traverse(1)
            else:
                # if we are not escaping a quote, flip 'escaped' and skip the character
                escaped = not escaped
                continue

        # a comma or \n marks the end of current value, unless within quotes, so append and continue
        if (split in character or linebreak in character) and not escaped:
            # add string to the row and reset
            row.append(string)
            string = ''
            if linebreak in character:
                yield row
                row = []
            continue

        # if we have made it this far, the character is plaintext and so append it to the current string
        string += character

    # if the file doesn't end on a newline, we need to append the final item then yield the row
    if string:
        row.append(string)
        return row


def set_types(s: str):
    """Converts a string, s, into the most suitable type"""
    for type_ in (int, float, str):
        try:
            # attempt to set the type
            return type_(s)
        except ValueError:
            # move on to the next type if failed
            pass


def safe_division(numerator, denominator, default=0) -> float:
    """Attempts to divide two numbers and returns a default value if the attempt fails"""
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return default


def round_output(places: int):
    """Decorator function that rounds all the outputs of the function it decorates to 'places' decimal places"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            def round_through(items):
                def round_(float_): return round(float_, places) if isinstance(float_, float) else float_
                def is_list(item): return type(item) in (list, tuple)

                # Recursively loop through 'items' and it's sub-lists, returning them round to the specified length
                type_ = type(items)
                return type_(round_(item) if not is_list(item) else round_through(item) for item in items)

            # Round the output of the decorated function and return it
            func_out = func(*args, **kwargs)
            return round_through(func_out)
        return wrapper
    return decorator


@round_output(4)
def main(file: str, target_region: str):
    """
    Function that processes a CSV file containing country data. Returns the following outputs:
        1.  A list containing two elements, being the countries that have the maximum and minimum population out of
            the countries who are both in the target region and have a yearly net change greater than zero
        2.  A list containing two elements; one of which is the average population of the target region, the other
            being the standard deviation of the same region
        3.  A list containing a sublist for each country in the region, containing both the name of the country and its
            density, eg ['China', 156], sorted by density in descending order
        4.  A float describing the correlation coefficient between population and land area for the region
    """

    # Open the file
    with open(file, 'r') as csv_file:
        reader = csv_read(csv_file)

        # initialise the variables/dictionaries that will be used to read the file
        populations, areas, net_changes, densities = dict(), dict(), dict(), dict()
        population_total, area_total = 0, 0

        num_countries = 0
        for num, line in enumerate(reader):

            # If this is the first row in the file, establish the header
            if not num:
                header = {pos: heading for pos, heading in enumerate(line)}
                continue

            # Create a dictionary that maps the current row to the header names
            items = (set_types(column) for column in line)
            current = {header[pos]: item for pos, item in enumerate(items)}

            # Set all the necessary variables
            name, population, net_change, area, region = current['Name'], current['Population(2020)'], \
                current['Net Change'], current['Land Area'], current['Regions']

            if region == target_region:
                # add pop/area to their respective dictionary, then add that value to the total
                population_total += population
                populations[name] = population
                area_total += area
                areas[name] = area

                # add the net change and density to their respective dictionaries
                net_changes[name] = net_change
                densities[name] = population / area

                num_countries += 1

        # if there were no lines found, raise an error
        if not num_countries:
            raise ValueError('No such region!')

        average_population, average_area = population_total / num_countries, area_total / num_countries
        pop_diff, area_diff, pop_area_diff = 0, 0, 0

        # Loop over both dictionaries, summing the needed values for standard deviation and correlation
        for population, area in zip(populations.values(), areas.values()):
            pop_diff += (population - average_population) ** 2
            pop_area_diff += (population - average_population) * (area - average_area)
            area_diff += (area - average_area) ** 2

        # Construct dictionary containing the name and population of the countries with a positive net change
        valid_populations = {name: populations[name] for name, change in net_changes.items() if change >= 0}
        # Sort the countries by population, from highest -> lowest
        valid_populations = sorted(valid_populations, key=valid_populations.get, reverse=True)
        # The max and min are the first and last items in valid_populations, respectively
        max_min = [valid_populations[0], valid_populations[-1]]

        # Both pop_st_d and correlation use safe_division, which returns a value should the result be undefined.
        # This means that should something strange happen (one country in region, all countries have same pop/area)
        # The function will still return an output. In this case it will return 0, as that is the logically correct
        # interpretation for all countries being identical.
        population_st_d = safe_division(pop_diff, len(populations) - 1) ** 0.5
        correlation = safe_division(pop_area_diff, (pop_diff * area_diff) ** 0.5)

        sorted_densities = [[name, densities[name]] for name in sorted(densities, key=densities.get, reverse=True)]

        # Return the outputs. We are done here :D
        return max_min, [average_population, population_st_d], sorted_densities, correlation


if __name__ == '__main__':
    print(main('countries.csv', 'Africa'))
