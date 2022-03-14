def triangleType(a, b, c):
    isATriangle = False
    if (a < b + c) and\
            (b < a + c) and\
            (c < a + b):
        isATriangle = True
    if isATriangle:
        if (a == b) and (b == c):
            print("the triangle was a EQUILATERAL")
        elif (a != b) and \
                (a != c) and \
                (b != c):
            print("the triangle was a SCALENE")
    else:
        print("invalid")

triangleType(3, 5, 8)