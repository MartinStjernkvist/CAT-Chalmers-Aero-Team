import numpy as np

"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
BUDGET CALCULATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

"""
NUMBER OF PEOPLE
"""
SARC = 10
industry = 50
university = 10
students = 25

number_of_people = SARC + industry + university + students

"""
FOOD
costs per person
"""

# Coffee: 3 cups / person
# 450 g = 65 cups
# say 60 SEK per pack
coffee = 3 * (60 / 65)

# Fruit:
# 2 fruits / person
# Around 5 SEK per fruit, see coop prices
fruit = 10

# Catering:
# This can vary A LOT, depending on what we choose
# Or rather IF we choose to include it
catering_high = 120  # actual food, just a guesstimate
catering_low = 50  # baguette

# Sausages for grilling: regular & vegetarian
# https://handlaprivatkund.ica.se/stores/1004219/search?q=grillkorv
# Let's ball out, some quality stuff
# Around 110 SEK / kg.
# Say 200 g / person.
sausage = 22
bread = 30 / 4
topping = 3
grill = sausage + bread + topping

# Mingelbricka:
# https://www.ica.se/catering/maxi-ica-stormarknad-vastervik-1003568/buffer/mingelbricka/
# Cost: 139 per plate
mingeltallrik = 139 / 5

# Bakery:
# 1 cinnamon bun
# Maybe something else
cinnamon_bun = 15
bakery = cinnamon_bun

"""
TOTAL BUDGET
"""

# Total FOOD
total_food_high = coffee + fruit + catering_high + grill + mingeltallrik + bakery
total_food_low = coffee + fruit + catering_low + grill + mingeltallrik + bakery

total_budget_high = number_of_people * total_food_high
total_budget_low = number_of_people * total_food_low

print(f'\nTotal budget, high (SEK): {round(total_budget_high)}')
print(f'Total budget, low (SEK): {round(total_budget_low)}')
