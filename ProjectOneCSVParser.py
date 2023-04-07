with open('countries.csv', 'r') as file:

    # Initialise variables
    string = ''
    data = []
    line = []
    index = 0

    # read the first character in the file.
    char = file.read(1)

    # while there are unread characters in the file:
    while char:

        # get current char
        file.seek(index)
        char = file.read(1)

        # update index now; statements break loop so can't increment at end
        index += 1

        # skip double quotes
        if '\"' in char:
            continue

        # a comma marks a new item in row, so append current string and move on to next char
        if char in ',':
            line.append(string)
            string = ''
            continue

        # \n marks end of a row, so append row to data and reset
        if char in '\n':
            line.append(string)
            data.append(line)
            line = []
            string = ''
            continue

        # if we have made it this far, the char is plaintext and so append it to the current string
        string += char
