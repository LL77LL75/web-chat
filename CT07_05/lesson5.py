# Lesson 5 - List Variables II

## Recap 1: Favourite Food List
# **Recap 1a**:
# Create a list of 5 foods that you like to eat
# foods = ["pizza","chips","ice cream","banana"]

# **Recap 1b**:
# You no longer like to eat the 3rd item on your list,
# delete it
# foods.pop(2)
# **Recap 1c**:
# Add 1 more item into your list
# foods.append("poop")
# **Recap 1d**:
# Write a for loop to say all the food items in your list
# for i in range(len(foods)):
#     print(foods[i])

# for food in foods:
#     print(food)

## Task 1: List of 100 numbers 
# You are preparing for an upcoming lucky draw session at your
# school. You have been tasked to create a program that will pick
# 100 lucky winners.
# import random
# By importing the 'random' library and using 'random.randint()',
# create a program to create 100 random numbers in a list
# 1. Use a loop to add 100 random numbers into your list.
# 2. Each number added range between 1 to 1000
# b = []
# for i in range(100):
#     b.append(random.randint(1,1000))
# print(b)

## Task 2: List of 100 unique numbers
# The program you have created from the previous task will
# sometimes generate duplicate numbers. Modify your program so
# that the 100 numbers generated are all unique.

# Modify your program from the previous task to create 100 random
# unique numbers in a list.
# 1. Use a loop to add 100 random numbers into your list.
# 2. Each number added range between 1 to 1000
# 3. Ensure that all the numbers are unique
# 4. Print the list of 100 unique numbers created