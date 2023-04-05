def chunk(s, v):
    if s[0:1] is v or not s:
        return ''
    return s[0] + chunk(s[1:], v)


def read_line(line, new=',', quotechar='\"'):
    out = []
    numeric = '1234567890.-'

    while line:
        if line[0] is not quotechar:
            c = chunk(line, new)
            if all(chars in numeric for chars in c.strip()):
                try:
                    c = int(c)
                except ValueError:
                    c = float(c)
            c = c, 1
        else:
            c = chunk(line[1:], quotechar), 3

        out.append(c[0])
        line = line[len(str(c[0])) + c[1]:]

    return out


with open('countries.csv', 'r') as csvfile:
    csvread = read(csvfile)
    for row in csvread
        print(row)
