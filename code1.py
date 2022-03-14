# EX1
# if x < y:
#     y = 0
#     x = x + 1
# else:
#     x = y

def max(a, b, c):
    if a > b and a > c:
        print(a,' is maximum among all')
    elif b > a and b > c:
        print(b, ' is maximum among all')
    else:
        print(c, ' is maximum among all')

max(30, 28, 18)

# def triangleType(a, b, c):
#     isATriangle = False
#     if (a < b + c) and\
#             (b < a + c) and\
#             (c < a + b):
#         isATriangle = True
#     if isATriangle:
#         if (a == b) and (b == c):
#             print("the triangle was a EQUILATERAL")
#         elif (a != b) and \
#                 (a != c) and \
#                 (b != c):
#             print("the triangle was a SCALENE")
#     else:
#         print("invalid")
#
# triangleType(3, 5, 8)

# def testfunc(x, y):
#     if x >= 0 and y >= 0:
#         if y*y >= x*10 and y <= math.sin(math.radians(x*30))*25:
#             if y >= math.cos(math.radians(x*40))*15:
#                 print('oooookk')
# testfunc(2, 3)


# EX2
# if (x < y):
#     y = 0
#     x = x + 1

# EX3
# if x < y:
#     return
# print(x)
# return

# EX4
# x = 0
# while (x < y):
#     y = f(x,y)
#     x = x + 1


# EX5
# for x in range(10):
#     y = f(x,y)


# a = [2 * x for x in y if x > 0 for y in z if y[0] < 3]

#




# digits = [0, 1, 5]
# a = 0
#
# for i in digits:
#     a += i
#     if i == 5:
#         print("5 in list")
#         break
# else:
#     print("out of the loop")


# try:
#     b = b + 5
# except KeyError:
#     a += 1
# except ZeroDivisionError:
#     a += 2
# else:
#     a += 3
# finally:
#     b += 1
#     a = a - b

#
# x = 0
# while(x < y):
#     y = f(x, y)
#     if(y == 0):
#         break
#     elif(y < 0):
#         y = y * 2
#         continue
#     x = x + 1
