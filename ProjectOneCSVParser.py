def next_char(file) -> str:
    """Returns the next character in a file without increasing the index"""
    char = file.read(1)
    file.seek(file.tell() - 1)
    return char


def prev_char(file) -> str:
    """Returns the previous character in a file without decreasing index"""
    index = file.tell()
    try:
        file.seek(file.tell() - 2)
        char = file.read(1)
    except ValueError:
        char = None
    file.seek(index)
    return char


def set_type(s):
    """Converts a string, s, into the most suitable type"""
    for set_types in [int, float, str]:
        try:
            return set_types(s)
        except ValueError:
            pass


def csv_read(file, split=',', linebreak='\n', escape='\"') -> list:
    """Generator Function that yields the lines of a CSV file as a list, one line at a time"""

    # Initialise variables
    string = ''
    char = ' '
    row = []
    escaped = False

    # while there are unread characters in the file:
    while char:

        # get current char
        char = file.read(1)

        # skip double quotes, make note that we have seen double quotes, then continue
        if escape in char:
            # if the next character is a double quote also, then rather than escaping the line we append a double quote
            if escape in next_char(file):
                # skip the next character, so as not to prematurely close the escape
                # however we don't continue, so that char is still appended
                file.read(1)
            else:
                # if we are not escaping a quote, continue as normal
                escaped = not escaped
                continue

        # a comma marks a new item in row, so append current string and move on to next char, unless within quotes
        if split in char and not escaped:
            # if we are not within quotes, match the type from string to whatever is best suited
            if escape not in prev_char(file):
                string = set_type(string)
            # add string to the row and reset
            row.append(string)
            string = ''
            continue

        # \n marks end of a row, so yield row and reset, unless within quotes
        if linebreak in char and not escaped:
            row.append(string)
            yield row
            row = []
            string = ''
            continue

        # if we have made it this far, the char is plaintext and so append it to the current string
        string += char
