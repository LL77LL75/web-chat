HINTS_FILE = "hints.txt"
authorisations_file = "authorisations_codes.txt"
with open(authorisations_file, "r") as f:
    global codes
    codes = f.read().splitlines()
command = ""
code = ""
with open(HINTS_FILE) as f:
    hints = int(f.read())
user_guess = ""
win = False
word = ""
with open("FiveLetterWords.csv","r") as f:
    content = f.read()
    words = content.split(",")
import random
cWord = random.choice(words)
def evaluate_guess(user_guess, cWord, wordlist):
    eval = ""
    for i in range(5):
        if user_guess[i] == cWord[i]:
            eval += user_guess[i]
        elif user_guess[i] in cWord:
            eval += "?"
        else:
            eval += "#"
    if user_guess != cWord:
        print("evaluation>> " + eval)
    

def validate(user_guess, wordlist):
    if user_guess == "commands":
        global command
        command = input("Enter a command: ")
        if command == "add hint" or command == "add hints":
            code = input("Enter the code: ")
            if code in codes:
                with open(HINTS_FILE, "w") as f:
                    f.write(str(input("how many hints do you want to add?")))
            if command == "reset hints" or command == "reset hint":
                code = input("Enter the code: ")
                if code in codes:
                    with open(HINTS_FILE, "w") as f:
                        f.write("0")
            if command == "set hints" or command == "set hint":
                code = input("Enter the code: ")
                if code in codes:
                    with open(HINTS_FILE, "w") as f:
                        f.write(str(input("how many hints do you want to set?")))
    elif not user_guess.isalpha():
        print("enter a 5-letter word BEEP BEEP BOOP BOOP")
        return False
    elif len(user_guess) != 5:
        print("enter a five-letter word BEEP BEEP BOOP BOOP")
        return False
    elif user_guess not in wordlist:
        print("enter a real five-letter word BEEP BEEP BOOP BOOP")
        return False
    else:
        return True

def get_guess(wordlist):
    while True:
        user_guess = input("your guess>> ").lower()
        if user_guess == "restart":
            return "restart"
        elif user_guess == "help":
            print("enter a five-letter word, or type 'restart' to restart the game, or 'quit' to quit.")
        if user_guess == "hint":
            print("the word contains the letter: " + random.choice(cWord))
            hints -= 1
            print("You have " + str(hints) + " hints left.")
        if validate(user_guess, wordlist):
            return user_guess
print(cWord)
def play_game():
    global hints
    global cWord
    global win
    win = False
    cWord = random.choice(words)
for i in range(6):
    if user_guess == "restart":
        cWord = random.choice(words)
        i = 0
        print("game restarted")
    print("guess " + str(i+1) + " of 6")
    user_guess = get_guess(words)
    evaluate_guess(user_guess, cWord, words)
    if user_guess == cWord:
            print("You win!")
            win = True
            hints += 1
            with open(HINTS_FILE, "w") as f:
                f.write(str(hints))
            print("you have " + str(hints) + " hints now")
            break
if win == False:
    print("You lose! The word was: " + cWord)
