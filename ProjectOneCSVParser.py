class BufferedReader:

    def __init__(self, file, size):
        if size < 1:
            raise ValueError('Buffer size must be greater than or equal to 1')
        self.file = file
        self.file.seek(0)
        self.buffer_size = size
        self.buffer = self.fill_buffer(self.buffer_size)

        # index set to minus 1 so that the first call of __next__ or .peek() returns self.buffer[0]
        self.index = -1

    def __iter__(self):
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
        # read the number of characters equal to size plus one
        self.index = 0
        return self.file.read(size + 1)

    def traverse(self, k) -> None:
        self.index += k
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


def csv_read(file, split=',', linebreak='\n', escape='\"'):
    """Generator Function that yields the lines of a CSV file as a list, one line at a time"""

    # The Buffer size is simply a sufficiently large number
    # Any value would work but large ones reduce the times the file has to be accessed and is hence faster
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
            row.append(set_types(string))
            string = ''
            if linebreak in character:
                yield row
                row = []
            continue

        # if we have made it this far, the character is plaintext and so append it to the current string
        string += character

    # if the file doesn't end on a newline, we need to append the final item then yield the row
    if string:
        row.append(set_types(string))
        return row


def set_types(s):
    """Converts a string, s, into the most suitable type"""
    for set_type in [int, float, str]:
        try:
            # attempt to set the type
            return set_type(s)
        except ValueError:
            # move on to the next type if failed
            pass


def main(file, target_region):

    # Open the file
    with open(file, 'r') as csv_file:
        reader = csv_read(csv_file)

        # initialise the variables/dictionaries that will be used to read the file
        populations = dict()
        population_total = 0
        areas = dict()
        area_total = 0
        net_changes = dict()
        densities = dict()

        num = 0
        for line in reader:
            name, population, yearly_change, net_change, area, region = line

            if region == target_region:
                # add pop/area to their respective dictionary, then add that value to the total
                population_total += population
                populations[name] = population
                area_total += area
                areas[name] = area

                # add the net change and density to their respective dictionaries
                net_changes[name] = net_change
                densities[name] = population / area

                num += 1

        # if there were no lines found, raise an error
        if not num:
            raise ValueError('No such region!')

        av_pop, av_area = population_total / num, area_total / num
        pop_diff, area_diff, pop_area_diff = 0, 0, 0

        # Loop over both dictionaries, summing the needed values for standard deviation and correlation
        for population, area in zip(populations.values(), areas.values()):
            pop_diff += (population - av_pop) ** 2
            pop_area_diff += (population - av_pop) * (area - av_area)
            area_diff += (area - av_area) ** 2

        positive_changes = {name: populations[name] for name, change in net_changes.items() if change >= 0}
        max_min = [max(positive_changes, key=positive_changes.get), min(positive_changes, key=positive_changes.get)]

        population_sd = (pop_diff / (len(populations) - 1)) ** 0.5
        sorted_densities = [[name, round(densities[name], 4)] for name in sorted(densities, key=densities.get)[::-1]]
        correlation = round(pop_area_diff / (pop_diff * area_diff) ** 0.5, 4)

        return max_min, [round(av_pop, 4), round(population_sd, 4)], sorted_densities, correlation


if __name__ == '__main__':
    for item in main('countries.csv', 'Africa'):
        print(item)
