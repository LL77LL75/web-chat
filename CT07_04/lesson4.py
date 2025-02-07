# a = 11
# import time
# while a >1:
#     time.sleep(1)
#     a-=1
#     print(a)
# print("happy New year!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

## Task 3: Flight Round the Globe
# Task: Write a program to keep track of the countries you
# are visiting.

# 1. Use a while loop to ask the user what country they
#    would like to visit.
# 2. Add the country into a list
# 3. If the user types "end", exit the loop
# 4. Print all the countries in the list in this format.
#    "I would like to visit Germany"
#    "I would like to visit Japan"
#    ... 
# goto = []
# answer = input("where u want to go ")
# while answer != "end":
#     goto.append(answer)
#     answer = input("where u want to go ")
# for i in goto:
#     print("i woul like to go to " + i )

## Task 4: Restaurant Menu
# **Task 4a**:
# Write a program to create a menu for a new
# restaurant

# 1. Using a while loop, ask the user (the restaurant manager)
#    to input food items
# 2. Add each food item into the menu list
# 3. End the loop when the user types "end"

# **Task 4b**:
# Based on the list created by the restaurant manager, do
# the following:

# 1. Imagine a customer has come in, ask the customer what
#    would they like to eat?
# 2. If the food is in the list, say "Yes we sell that,
#    please have a seat"
# 3. else, say "Sorry, please go next door, bye."
want = [pizza,]
answer = input("wat u want to eat")
while answer != "end" and answer in want:
    print("We sell that.Now take a seat in the definitely not eletric chair")
else:
    print("sorry we don't sell that and couldn't murder you")