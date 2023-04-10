class BufferedReader:

    def __init__(self, file, size):
        if size < 1:
            raise ValueError('Buffer size must be greater than or equal to 1')
        self.file = file
        self.buffer_size = size
        self.buffer = self.fill_buffer(self.buffer_size)

        # index set to minus 1 so that the first call of __next__ or .peek() returns self.buffer[0]
        self.index = -1

    def __iter__(self):
        return self

    def __next__(self) -> str:
        self.index += 1
        if self.index >= self.buffer_size:
            self.buffer = self.fill_buffer(self.buffer_size)
            self.index = 0
        try:
            char = self.current()

            self.current()
        except IndexError:
            raise StopIteration
        return char

    def fill_buffer(self, size) -> str:
        # read the number of characters equal to size, and then one additional so that .peek() will always
        buffer = self.file.read(size + 1)
        # move the cursor back 1 so that the next buffer still starts from the correct place
        self.file.seek(self.file.tell() - 1)
        return buffer

    def traverse(self, k) -> None:
        self.index += k

    def current(self) -> str:
        return self.buffer[self.index]

    def peek(self) -> str:
        # attempt to return the next item in buffer. If it doesn't exist, return null
        try:
            return self.buffer[self.index + 1]
        except IndexError:
            return '\0'


def set_types(s):
    """Converts a string, s, into the most suitable type"""
    for set_type in [int, float, str]:
        try:
            # attempt to set the type
            return set_type(s)
        except ValueError:
            # move on to the next type if failed
            pass


def csv_read(file, split=',', linebreak='\n', escape='\"'):
    """Generator Function that yields the lines of a CSV file as a list, one line at a time"""

    # Initialise variables
    file = BufferedReader(file, 1000)
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
                # if we are not escaping a quote, continue as normal
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


if __name__ == "__main__":
    with open('countries.csv', 'r') as csv_file:
        reader = csv_read(csv_file)
        for line in reader:
            print(line)
