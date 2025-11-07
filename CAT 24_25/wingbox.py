from imports import *

g = 9.82

# L = 150 * 3 / 2
# B = 2.6 / 2 * g
# print(B)
# W = (15 - 2.6) / 2 * g
#
# e = 0.7
# f = (2 - 0.16) / 2
# print(f)
# c = 0.485
# d = 0.1
#
#
# R_y = L - W - S_y - B
#
# M_0 = S_y * c + B * e - L * f
# M = M_0 + R_y * d
#
# V = R_y
#
# print(M)
# print(V)
# print(S_y)

# N

"""
L = 150 * 3 / 2
B = 2.6 / 2 * g
W = (15 - 2.6) / 2 * g
print(W)

# m
e = 0.7
f = (2 - 0.16) / 2
c = 0.485
d = 0.1

# Antagande
# S_y = 1/2 * (L - B - W)
S_y = 0
print(S_y)

M_0 = L * f - B * e - S_y * c
R_y = S_y + B + W - L

V = R_y
M = M_0

print()
print(M_0)
print(V)
"""

# L = 225
# l1 = 70/2
# l2 = 485-l1
# l3 = (2000 - 160) / 2 - l2 - l1
#
# R = L * l3 / l2
# print(R)

# Nytt försök
l_wing = 2000
l_wingbox = 70
l_strut = 70 + 480 + 10 / 2
l_batteries = 70 + 560 + 160 / 2
l_lift = 90 + (l_wing - 90) / 2
print('\nl_strut: ', l_strut)
print('l_strut: ', l_batteries)
print('l_strut: ', l_lift)

Acceleration = 3 * 9.82
F_lift = (15 / 2) * Acceleration
F_batteries = 1.6 * Acceleration
W_structure = 1 * Acceleration
W_wingbox = 0.3 * Acceleration
W_rest = (15 / 2) * Acceleration - F_batteries - W_structure - W_wingbox
print('\nF_lift: ', F_lift)
print('F_batteries: ', F_batteries)
print('W_self: ', W_structure)
print('W_wingbox: ', W_wingbox)
print('W_rest: ', W_rest)

R = 1 / (l_strut - l_wingbox / 2) * (F_lift * (l_lift - l_strut) - F_batteries * (l_batteries - l_strut) - W_structure * (l_wing/2 -l_strut))
print('\nR: ', R)

equiv = R * (l_strut - l_wingbox / 2) / (l_wing - l_wingbox/2)
print('equiv: ', equiv)
