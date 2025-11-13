import re

def test(m):
    print('hhhh',m["count"])
    x = int(m["count"])+1
    return str(x)
#lambda m: str(int(m.group()) + 1)

xx = 'c:\\tets\\test_0.csv'
while xx != "c:\\tets\\test_999.csv":
    r = re.sub(r'(?<=\_)(?P<count>[0-9]{1,3})(?=\.csv|\.json)', lambda m: str(int(m.group('count')) + 1) if int(m.group('count')) < 999 else m.group('count'), xx)
    xx = r
    print(r)                                                       #lambda m: str(int(m.group('count')) + 1) if int(m.group('count')) < 999 else m.group('count')

#r = re.sub(r'(?<=\_)(?P<count>[0-9]{1,3})(?=\.csv|\.json)', test, "c:\\tets\\test_0.csv")
print(r)