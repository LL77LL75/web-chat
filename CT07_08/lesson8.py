import random
hp = 100
battles = 0
# sets the hero's health points
while hp >0:
    print("after fighting monsters the hero has " + str(hp) + "health left")
    # reduces the hero's health
    hp = hp - random.randint(1,5)
    #checks if the hero has more than 0 health
    battles += 1
print("the hero died after fighting " + str(battles) + " battles")