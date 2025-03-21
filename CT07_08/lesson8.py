# # Lesson 8 - String splitting, list joining, and
# #            finding substring

# ## Recap 1: List Manipulation
# Given 3 lists, merge them into a single list, remove
# duplicates, and then split the list into 2 halves,
# ensuring both halves are sorted.

# list1 = [3, 2, 1]
# list2 = [6, 5, 5]
# list3 = [9, 8, 7]

# 1. Merge the 3 lists and remove duplicates.
# 2. Sort the resulting list.
# 3. Split the list into 2 sorted halves.
# 4. Print the halves.
# 5. 
# pw = input("password ")
# if len(pw)>8:
#     if (pw.isupper() and pw.islower()):
#         print("password not accepted")
#     else :
#         if (pw.isalpha() and pw.isdigit()) :
#             print("password not accepted")
#         else:
#             print(" your password is secure")
# word = input("words")
# letters = ""
# count = 1
# for i in word:
#     if count % 2 == 0:
#         letters += i.upper()
#         count+=1
#     else:
#         letters += i.lower()
#         count+=1
# print(letters)
# list =  ['Computers', 'empower', 'our', 'modern', 'world', 'with', 'their', 'digital', 'brains.']
# word = ",".join(list)
# sentance= "Hello World"

# for i in sentance:
#     i



## Task 6: Checking if a Word is a Palindrome
# Write a program to check if the word "radar" is a palindrome.
# A word is a palindrome if it reads the same backward as forward.

# Example:
# Input: "radar"
# Output: True



## Task 7: Checking user input for Palindrome
# Create a while loop that will endlessly ask user for a word and
# check if the word is a Palindrome.

# The while loop will end when user says "end"

# Output:
# 1 palindrome detected: 
# a
# inputt = input("WOT U WANT ")
# reversed = inputt[::-1]
# while not (inputt == "end"):
#     if reversed == inputt:
#         print("it is a palindrome")
#         inputt = input("WOT U WANT ")
#         reversed = inputt[::-1]
#     else:
#         print("it is as good as a fart")
#         inputt = input("WOT U WANT ")
#         reversed = inputt[::-1]
        



## Task 8: Checking user input for presence of Palindrome
# Create a program that will check if a palindrome exists in a
# sentence.

### Example:
# Input:
# Enter a sentence: <<"This is a sentence, check for palindrome">>

