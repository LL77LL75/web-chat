
word = ""
with open("FiveLetterWords.csv","r") as f:
    content = f.read()
    words = content.split(",")
import random
cWord = random.choice(words)
def getWord(wordList):
    while True:
        global word
        word = input("your guess>>> ")


guess = input("your guess>> ")
def evaluate_guess(guess,cWord,wordlist):
    eval = ""
    for i in range(5):
        if guess[i] == cWord[i]:
            eval+= guess[i]
        elif guess[i] in cWord:
            eval+= "?"
        else:
            eval+="#"
    print(eval)
def validate(guess,wordlist):
    if not guess.isalpha():
        print("enter a 5-letter word BEEP BEEP BOOP BOOP")
        return False
    elif len(guess)!=5:
        print("enter a five-letter word BEEP BEEP BOOP BOOP")
        return False
    elif not guess in wordlist:
        print("enter a real five-letter word BEEP BEEP BOOP BOOP")
        return False
    else:
        return True

getWord(words)
for i in range(6):
    evaluate_guess(guess,cWord,words)
    guess = input("your guess>>")