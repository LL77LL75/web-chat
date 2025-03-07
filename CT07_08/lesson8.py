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