classes = [
    ["Asher", "Bob", "Charles"],
    ["Dan", "Esther", "Frank"],
    ["Gina", "Hannah", "Ian"]
]

# Q1 Print out Frank
print(classes[1][2])
classes[2][1] = "heather"
# Q2 Change Hannah to Heather

# Q3 Using list slicing and list concatenation, output the following sublist:
# ["Asher", "Bob", "Dan", "Esther"]
print(classes[0][0:2]+classes[1][0:2])
# Q4 Using a for loop, get the list of students in class who are also awardees
# Define a function flatten(...) that takes a 2d list and returns a 1d list
# Define a function intersect(..., ...) that takes 2 1d lists and returns the common elements in a list
# Using flatten and intersect, get the answer 



# Q5 Statistics
# 1. Generate 100 random numbers from 1 - 100 into a list.
# 2. Partition them into 2 lists, even and odd
# 3. For each list, get the smallest, largest, and mean value
# Sample output
# Odd - Smallest: 3, Largest: 91, Mean: 52.375, Length: 48
# Even - Smallest: 8, Largest: 100, Mean: 49.0, Length: 52