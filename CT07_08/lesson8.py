ans = input("what would you like to order? ")
#asks the user what he/she wants to order
order = []
#allows the orders to be stored
while ans != "end":
    order.append(ans)
print("you have ordered the following:")
for i in order:
    print()