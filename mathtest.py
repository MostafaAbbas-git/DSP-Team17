import numpy as np
import cmath
import math

# z = np.complex(3, 4)  # A complex number, 3+4i
# w = cmath.polar(z)

# # printing modulus and argument of polar complex number
# print("The modulus and argument of polar complex number is : ", end="")
# print(w)

# converting complex number into rectangular using rect()
# w1 = cmath.rect(5.0, 0.9272952180016122)

# printing rectangular form of complex number
# print("The rectangular form of complex number is : ", end="")
# print(w1)
# c = np.complex(-1.16369012e+05,-1.28743776e+05)
# print("z: ", z)
# print("z phase: ", np.angle(z, deg=False))
# print("z mag: ", np.abs(z))
# print("z imag: ", np.imag(z))
# print("z real: ", np.real(z))
a = np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]])

b= np.array([[120, 121, 120, 120, 121],[43, 170, 50, 80, 90]])


nprect = np.vectorize(cmath.rect)

c = nprect(a, b)
print("c: ", c)
# print("c: ", c)
# print("c phase: ", np.angle(c, deg=False))
# print("c mag: ", np.abs(c))
# print("c imag: ", np.imag(c))
# print("c real: ", np.real(c))
# print("c re-multiplied imag and real: ", np.multiply(np.imag(c), np.real(c)))
# print("c re-multiplied phase and mag: ", np.multiply(np.abs(c), np.angle(c)))
