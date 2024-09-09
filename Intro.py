s1 = 1234

def add_strings(z):
    global s1
    if type(s1) != 'str':
        s1 = str(s1)
    m = z + s1
    return m

print(__name__)

if __name__ == '__main__':
    output = add_strings("Hello.")

    print(output)

