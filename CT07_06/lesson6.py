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
import random
winners = []
item = random.randint(1,100)
while len(winners) < 101:
    if item not in winners:
        winners.append(item)
print(winners)
print(len(winners))


