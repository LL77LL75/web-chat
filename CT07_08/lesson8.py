import random
hp = 100
# sets the hero's health points
while hp >0:
    #checks if the hero has more than 0 health
    hp = hp - random.randint(1,5)
    # reduces the hero's health
    print("after fighting monsters the hero has " + str(hp) + " left")
print("the hero")