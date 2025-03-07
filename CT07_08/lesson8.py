ans = input("what would you like to order? ")
#asks the user what he/she wants to order
order = []
#allows the orders to be stored
while ans != "end":
    
    order.append(ans)
    #adds the orderans = input("what would you like to order? ")
print("you have ordered the following:")
#prints the order
for i in len(order):
    print(str(i) + str(order[i]))