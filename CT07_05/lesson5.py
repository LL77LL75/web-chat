# Lesson 5 - List Variables II

## Recap 1: Favourite Food List
# **Recap 1a**:
# Create a list of 5 foods that you like to eat
foods = ["pizza","chips","ice cream","banana"]

# **Recap 1b**:
# You no longer like to eat the 3rd item on your list,
# delete it
foods.pop(2)
# **Recap 1c**:
# Add 1 more item into your list
foods.append("poop")
# **Recap 1d**:
# Write a for loop to say all the food items in your list
for i in range(len(foods)):
    print(foods[i])