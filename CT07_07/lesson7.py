# Lesson 7 - 2 dimensional list

## Recap 1: Student Contact Database
# Task: Create a contact database for students
# 1. Create a list variable called students
# 2. Create 3 lists called student1, student2, student3
#     each student should have the following info:
#         1. name
#         2. phone number
#         3. CCA
# 3. Add student1, student2, student3 into the students list.
# 4. Unpack the list and use loop and string concatenation to
#    print the details for each student in the following format:

#    Name: James
#    Phone number: 85726845
#    CCA: Hockey

# student1 = ["John", 98453126, "Hockey"]
# student2 = ["Adam", 93029102, "Soccer"]
# student3 = ["Sylvia", 87894032, "Dance"]
# students = [student1,student2,student3]
# for student in students:
#     for student in students:
#         name,phone_number,cca = student
#     print(name)
    

## Task 1: Introduction to List Merging
# You are given 2 lists of fruits. Merge them into 1 list and
# print the result:

# list1 = ["Apple", "Banana", "Cherry"]
# list2 = ["Durian", "Elderberry", "Figs"]

# # 1. Use the + operator to combine the lists.
# # 2. Print the combined list.
# fruits = list1+list2
# print(fruits)

## Task 2: Ordered List Merging
# You are given 2 lists that contain the price of fruits. Now,
# merge 2 given lists and ensure the resulting list is sorted.

list1 = [3.20, 2.65, 1.75]
list2 = [6.15, 5.45, 4.20]
list3 = list1 +list2
# 1. Merge the lists using the + operator.
# 2. Use the sorted() function to sort the combined list.
# 3. Print the sorted list.
b = sorted(list3)
## Task 3: Splitting Lists at a Point
# You are required to divide a basket of fruits.
# Split the given list at the specified index:

fruits = ["Apple", "Banana", "Cherry", "Durian", "Elderberry", "Figs"]
index = 3

# 1. Use slicing to split the list at the provided index.
# 2. Print the resulting sublists.


## Task 4: Splitting a List in Half
# You have been tasked to divide the basket of fruits into
# 2 equal halves. Given a list of even length, split it
# into 2 equal halves.

# fruits = ["Apple", "Banana", "Cherry", "Durian", "Elderberry", "Figs"]

# 1. Find the midpoint of the list.
# 2. Split the list into 2 halves using slicing.
# 3. Print both halves.
# mid = len(fruits)//2
# print(fruits[:mid])
# print(fruits[mid:])

## Task 5: Identifying Common Elements in Lists
# You have been given 2 lists of fruits. However, there might be
# duplicates. Your job is to identify and print the common fruits
# between them.

list1 = ["Apple", "Banana", "Cherry", "Durian"]
list2 = ["Cherry", "Durian", "Elderberry", "Figs"]

# 1. Create an empty list named 'common'
# 2. Using 'for' loops, append common elements into 'common'
# 3. Print the common elements
common = []

for i in list1:
    for a in list2:
        if i == a :
            common.append(i)
