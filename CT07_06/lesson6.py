# Lesson 6 - 2-dimensional list

## Recap 1: List of 100 unique numbers
# **Recap 1a**:
# You are preparing for an upcoming lucky draw session at your
# school. However, there must be no repeating winning numbers.

# Task: Create a program to create 100 random unique numbers in
# a list
# 1. Use a loop to add 100 random numbers into your list.
# 2. Each number added range between 1 to 1000
# 3. Ensure that all the numbers are unique
# import random
# winners = []
# while len(winners) < 1000000000000000:
#     item = random.randint(1,10000000000000000)
#     if item not in winners:
#         winners.append(item)
# print(winners)

# **Recap 1b**:
# You have been asked to provide some statistics based on the
# list of numbers generated.

# 1. Using max(), find the highest number from the list
# 2. Using min(), find the lowest number from the list
# 3. Using sum() and len(), find the average from the list
# 4. By importing the 'random' library and using random.choice(),
#    print out a random number from the list.
# 5. Using index(), print out the index of the printed random
#    number.
# a = random.choice(winners)
# print("the max is " + str(max(winners)))
# print("the min is " + str(min(winners)))
# print("the average is " + str(sum(winners)/len(winners)))
# print("the choice is " + str(a) + " at index " + str(winners.index(a)))

## Task 1: A list within a list 

# You are about to graduate and would like to create a database
# to keep all your friend's contact details using a 2d list.

# Sample Code (Copy + Paste the below code):
# contacts = []
# contact1 = ["John", 98453126, "john@gmail.com"]
# contact2 = ["Adam", 93029102, "adam@gmail.com"]
# contact3 = ["Sylvia", 87894032, "sylvia@gmail.com"]

# 1. append contact1, contact2, and contact3 into contacts
# 2. Write a nested loop to loop through each contact and print
#    the details for each contact

# contacts = []
# contact1 = ["John", 98453126, "john@gmail.com"]
# contact2 = ["Adam", 93029102, "adam@gmail.com"]
# contact3 = ["Sylvia", 87894032, "sylvia@gmail.com"]
# contacts.append(contact1)
# contacts.append(contact2)
# contacts.append(contact3)
# for contact in contacts:
#     for detail in contact:
#         print(detail)


## Task 2: Student List
# You have been given a 2d list of students from a class
# consisting each student's name and their gender:

# Sample Code (Copy + Paste the below code):
students = [
    ["Olivia", "F"], ["Noah", "M"], ["Emma", "F"],
    ["Liam", "M"], ["Ava", "F"], ["Ethan", "M"],
    ["Sophia", "F"], ["Lucas", "M"], ["Mia", "F"],
    ["Aiden", "M"], ["Isabella", "F"], ["Jackson", "M"],
    ["Amelia", "F"], ["Logan", "M"], ["Lily", "F"]
]
for student in students:
    print(str(student[0]) +","+str(student[1]))
### the above is a nested list. Study and discuss it before we
### move on.

# 1. Write a for loop to print out the names of each student and
#    the gender beside.
   
#    e.g. Olivia F
#         Noah M
