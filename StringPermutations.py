def permutations(s):
    # if len(s) == 1:
    #     return s
    # else:
    #     current_character = s[0]
    #     next_characters = permutations(s[1:])
    #     perms = set()
    #     for i in range(0, len(s)):
    #         for char in next_characters:
    #             perms.add(char[0:i] + current_character + char[i:])
    #     return perms

    return s if len(s) == 1 else {char[0:i] + s[0] + char[i:] for char in permutations(s[1:]) for i in range(len(s))}


print(len(permutations('abcdefghij')))
