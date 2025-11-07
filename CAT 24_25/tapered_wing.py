from imports import *

diam_3d = 0.4 * 10 ** (-3)

num_layers_len = 2 / diam_3d
num_layers_leading = 2
len = 100 * 10**3
volume_3d = diam_3d * num_layers_leading * 2 * 100 * 10 ** (-3)
density_plastic = 400 * 10 ** (3)
density_balsa = 160 * 10 ** (3)
volume_rod = (12 * 10 ** (-3) / 2) ** 2 * pi * 2

mass_balsa = volume_rod * density_balsa + 17
mass_3d = volume_3d * density_plastic

print('balsa', mass_balsa, 'g')
print('3d', mass_3d, 'g')

# ans = 97077 / 1_000_000_000 * 800
# print(ans* 1000)
