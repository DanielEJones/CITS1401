def chunk(s, v):
    if s[0:1] is v or not s:
        return ''
    return s[0] + chunk(s[1:], v)


def read_line(s):
    out = []

    while s:
        if s[0] != '\"':
            c = chunk(s, ','), 1
        else:
            c = chunk(s[1:], '\"'), 3

        out.append(c[0])
        s = s[len(c[0])+c[1]:]

    return out


print(read_line('a,b,c,"delimiter is a , ",k,"1",1'))
