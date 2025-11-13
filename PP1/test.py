import re

def test(m):
    print(m)
    return m

r = re.sub(r'.*', test, "c:\\tets\test_0.csv")
print(r)