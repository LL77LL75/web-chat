
word = ""
with open("five_letter_words.csv","r") as f:
    content = f.read
    words = content.split(",")
import random
cWord = random.choice(words)
def getWord(wordList):
    while True:
        global word
        word = input("your guess>>> ")



def evaluate_guess(guess,cWord):
    while
    eval = ""
    for i in range(5):
        if guess[i] == cWord[i]:
            eval+= guess[i]
        elif guess[i] in cWord:
            eval+= "?"
        else:
            eval+="#"
print("a")