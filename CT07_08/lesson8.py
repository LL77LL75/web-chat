ans = input("what would you like to order? ")
#asks the user what he/she wants to order
order = []
#allows the orders to be stored
while ans != "end":
    order.append(ans)
    #adds the order
    ans = input("what would you like to order? ")
    #changes the answer
print("you have ordered the following:")
#prints the order

for i in order:
    print(str(order.index(i)) + "." + i)
# import random
# hp = 100
# battles = 0
# # sets the hero's health points
# while hp >0:
#     print("after fighting monsters, his health is now: " + str(hp))
#     # reduces the hero's health
#     hp = hp - random.randint(1,5)
#     #checks if the hero has more than 0 health
#     battles += 1
# print("the hero died after fighting " + str(battles) + " battles")