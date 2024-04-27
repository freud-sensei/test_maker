foo = ['a', 'b', 'c', '', '']
while "" in foo:
    foo.remove("")
    print(foo)