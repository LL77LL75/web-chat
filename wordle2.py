import time
import os
blow_off_list = ["OOPS MOMENT","WOMP WOMP","SKILL ISSUE","SMOOTH DISASTER"]
win_list = ["Genius move!","Impressive!","You nailed it!","Well played!","Masterful guess!"]
a = 1
# global font_size
# font_size = input("Enter desired font size for the terminal (e.g., 12, 14, 16): ")
# try:
#     font_size_int = int(font_size)
#     os.system(f'echo -e "\\033]50;SetFont=Monospace {font_size_int}\\007"')
#     os.system("clear")
# except ValueError:
#     print("Invalid font size. Using default.")

import random

HINTS_FILE = "hints.txt"
authorisations_file = "authorisation_codes.txt"
words_file = "FiveLetterWords.csv"

def sync_hints_file():
    os.system('git add hints.txt && git commit -m "Auto-commit" && git push origin main')

if not os.path.exists(HINTS_FILE):
    with open(HINTS_FILE, "w") as f:
        f.write("0")
    sync_hints_file()

if not os.path.exists(authorisations_file):
    with open(authorisations_file, "w") as f:
        f.write("error")

if not os.path.exists(words_file):
    with open(words_file, "w") as f:
        print("error")

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
with open(words_file,"r") as f:
    content = f.read()
    words = content.split(",")
cWord = random.choice(words)
def evaluate_guess(user_guess, cWord):
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
        global command,font_size
        print("add hint or add hints to add hints ")
        print("minus hint or minus hints to remove hints ")
        print("reset hints or reset hint to reset hints ")
        print("set hints or set hint to set hints ")
        # print("font size or fonts or font to change the font size ")
        print("abort to exit commands")
        command = input("Enter a command:")
        if command == "add hint" or command == "add hints":
            code = input("Enter the code: ")
            global add_hints
            add_hints = input("how many hints do you want to add? ")
            if code in codes:    
                with open(HINTS_FILE, "w") as f:    
                    f.write(add_hints)
                sync_hints_file()
                os.system("clear")
        elif command == "minus hint" or command == "minus hints":
            code = input("Enter the code: ")
            global minus_hints
            minus_hints = input("how many hints do you want to remove? ")
            if code in codes:
                with open(HINTS_FILE, "w") as f:
                    f.write(str(int(hints) - int(minus_hints)))
                sync_hints_file()
                os.system("clear")
        elif command == "reset hints" or command == "reset hint":
            code = input("Enter the code: ")
            if code in codes:
                with open(HINTS_FILE, "w") as f:
                    f.write("0")
                sync_hints_file()
                os.system("clear")
        elif command == "set hints" or command == "set hint":
            code = input("Enter the code: ")
            global set_hints
            set_hints = input("how many hints do you want to set? ")
            if code in codes:
                with open(HINTS_FILE, "w") as f:
                    f.write(set_hints)
                sync_hints_file()
                os.system("clear")
        # elif command == "font size" or command == "fonts" or command == "font":
        #     code = input("Enter the code: ")
        #     font_size = input("Enter desired font size for the terminal (e.g., 12, 14, 16): ")
        #     if code in codes:
        #         try:
        #             font_size_int = int(font_size)
        #             os.system(f'echo -e "\\033]50;SetFont=Monospace {font_size_int}\\007"')
        #             os.system("clear")
        #         except ValueError:
        #             print("Invalid font size. Using default.")
        elif command == "abort":
            print("Aborting commands.")
            return False
        elif command == "add code" or command == "add codes":
            code = input("Enter the code to add: ")
            if code not in codes:
                with open(authorisations_file, "a") as f:
                    f.write("\n" + code)
                print("Code added successfully.")
                sync_hints_file()
                print(codes)
                time.sleep(10)
                os.system("clear")
        elif command == "remove code" or command == "remove codes":
            code = input("Enter the code to remove: ")
            if code in codes:
                codes.remove(code)
                with open(authorisations_file, "w") as f:
                    f.write("\n".join(codes))
                print("Code removed successfully.")
                sync_hints_file()
                print(codes)
                time.sleep(10)
                os.system("clear")
        else:
            print("Invalid command. Please try again.")
            return False
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
    global hints
    global cWord
    global user_guess
    while True:
        user_guess = input("your guess>> ").lower()
        if user_guess == "restart":
            return "restart"
        elif user_guess == "help":
            print("enter a five-letter word, or type 'restart' to restart the game, or 'quit' to quit.")
        elif user_guess == "hint" and hints > 0:
            hints -= 1
            with open(HINTS_FILE, "w") as f:
                f.write(str(hints))
            sync_hints_file()
            print("the word contains the letter: " + random.choice(cWord))
            print("You have " + str(hints) + " hints left.")
        if validate(user_guess, wordlist):
            return user_guess
def play_game():
    global hints
    global cWord
    global win
    global a
    win = False
    a = 1
    cWord = random.choice(words)

print(f"{"#"*30:^30}")
print(f"{"#"}{"Welcome to Wordle!":^28}{"#"}")
print(f"{"#"*30:^30}")
print("You have 6 guesses to find the 5-letter word.")
while True:
    while a <= 6:
        if user_guess == "restart":
            cWord = random.choice(words)
            a = 1
            user_guess = ""
            print("game restarted")
        print("guess " + str(a) + " of 6")
        user_guess = get_guess(words)
        evaluate_guess(user_guess, cWord)
        a+=1
        if user_guess == cWord:
                print("You win! " + random.choice(win_list))
                win = True
                hints += 1
                with open(HINTS_FILE, "w") as f:
                    f.write(str(hints))
                sync_hints_file()
                print("you have " + str(hints) + " hints now")
                break
        if win == False and a == 7:
            print(random.choice(blow_off_list) +" the word was "+ cWord)
    continue_game = input("Do you want to play again? (yes/no): ").lower()
    if continue_game == "yes":
        play_game()
    if  continue_game != "yes":
        print("PIGGY")
        play_game()
    user_guess = ""
    win = False
    hints = int(open(HINTS_FILE).read())
    cWord = random.choice(words)
    print("New game started. You have " + str(hints) + " hints.")
    print("you have " + str(hints) + " hints now")
    if win == False and a == 6:
        print("You lose! The word was: " + cWord)
    continue_game = input("Do you want to play again? (yes/no): ").lower()
    if continue_game == "yes":
        play_game()
    if  continue_game != "yes":
        print("PIGGY")
        play_game()
    user_guess = ""
    win = False
    hints = int(open(HINTS_FILE).read())
    cWord = random.choice(words)
    print("New game started. You have " + str(hints) + " hints.")