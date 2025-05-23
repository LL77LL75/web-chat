# primary 6 boy rolling around on the floor screaming in the girl full body swimsuit that he was forced to wear cannot be taken off and is too tight.

# wordle_guide_student.py
# A guided version of the Wordle game project
# Fill in the blanks as you follow the lesson steps
word = ""
# ===================================================
# Task 1: Load Word List from File
# ===================================================
# "a: Load words from a file"
# Hint: Use with open(...) as f
#       Use .read() and .split() to get the word list
with open("FiveLetterWords.csv", "r") as f: 
    content = f.read()
    words = content.split(",")
# words = ...

# ===================================================
# Task 2: Pick a Random Word
# ===================================================
# TODO: Choose a random word from the list
import random

cword =random.choice(words)
def getWord(wordList):
    while True:
        global word
        word = input("your guess >>  ")
        if not word.isalpha(): # appl3
            print("ENTER A WORD BEEP BEEP BOOP BOOP")
        elif len(word) != 5:
            print("ENTER A FIVE LETTER WORD BEEP BEEP BOOP BOOP")
        elif not word in wordList:
            print("ENTER A REAL WORD BEEP BEEP BOOP BOOP")
        else:
            return word
# ===================================================
# Task 3: Validate User Input
# ===================================================
# Create a function getWord(wordlist) that:
# - asks the user for a 5-letter word
# - checks if it's:
#       made of letters
#       5 letters long
#       in the wordlist


# ===================================================
# Task 4: Evaluate the Guess
# ===================================================
# TODO: Write a function that checks each letter in the guess
# and compares it with the correct word
def evaluate_guess(guess, cword):
    eval = ""
    for i in range(5):
        if guess[i] == cword[i]:
            eval += str(guess[i])
        elif guess[i] in cword:
            eval += "?"
        else:
            eval += "#"
    return eval
# print(cword)


# ===================================================
# Task 5: Game Loop
# ===================================================
# TODO: Write the main game loop (6 chances)
# Good luck
for i in range(6):
    if evaluate_guess != cword:
        print("guess "+str(i+1)+" of 6:")
        print("evalulation >> " +evaluate_guess(getWord(words),cword))
    else:
        print("YOU WIN")
        break