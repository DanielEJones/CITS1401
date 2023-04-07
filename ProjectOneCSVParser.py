with open('countries.csv', 'r') as file:

    string = ''
    out = []

    for char in file.read():
        # if the current char is a comma or a newline, add the current string to the output list and continue
        if char in ',\n':
            out.append(string)
            # clear string in preparation for next element
            string = ''
            continue
        # add current char to the element string
        string += char
