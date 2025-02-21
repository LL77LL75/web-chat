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
