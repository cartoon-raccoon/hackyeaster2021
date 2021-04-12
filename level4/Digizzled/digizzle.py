import re
from itertools import product

pattern = re.compile('^he2021\\{([dlsz134]){9}\\}$')

def hizzle(s):
    s1 = 13
    s2 = 37

    for n in range(len(s)):
        s1 = (s1 + ord(s[n])) % 65521
        s2 = (s1 * s2) % 65521

    return (s2 << 16) | s1

def smizzle(a, b):
    return format(a, 'x') + format(b, 'x')

for s in product("dlsz134", repeat=9):
    string = "he2021{" + "".join(s) + "}"
    a = hizzle(string)
    b = hizzle(string[::-1])

    final = smizzle(a, b)

    #print(final, string)
    if final == "c5ab05ca73f205ca":
        print(final, string)
