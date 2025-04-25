# **Task 1a**: Initialise board
# Create an 'initialise_board()' function that returns a 3x3 Tic
# Tac Toe board using nested lists. Each item in each of the list
# holds a space (' ').

# The 3x3 nested list visualised:
# [[' ', ' ', ' '],
#  [' ', ' ', ' '],
#  [' ', ' ', ' ']]

# 1. Create an 'initialise_board()' function that does the
#    following
# 2. Create an empty list, 'board'
# 3. Using 'for' loop to iterate 3 times,
#         a. Create an empty list, 'row'
#         b. Using 'for' loop to iterate 3 times,
#                 i. Using '.append()', add a space (' ') into
#                    the list, 'row'.
#         c. Append ('.append()') the list, 'row' into the list,
#            'board' to create a nested list.
# 5. Return 'board'

# **Test case**
# Input:
#     print(initialise_board())
# Expected output:
#     [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]




# Task 2 Pseudocode
# for row in board:
#   for cell in row:
#     if cell is NOT space:
#       print content of cell
#     else:
#       print cell_number
#     if cell_number is not a multiple of 3:
#       print "|"
#     increase cell_number by 1
#   if cell number <= 9
#     print "----------"


## Task 12.3a (get_player_move)
# Using the algorithm provided, create a 'get_player_move'
# function with 1 parameter, 'board'.

# **Algorithm**
# move = int(move_input) - 1
# row = move // 3
# col = move % 3

# When called, the function must:
# 1. Ask player for a number between 1 and 9 (stored in
#    'move_input')
# 2. Apply the above algorithm to calculate the row and column
#    number
# 3. Assign 'X' to the selected cell

# **Main game loop**
# 1. Initialise a game board
# 2. Print the game board
# 3. Ask the user for a move
currentPlayer = ""
if random.randint(0,1) == 0:
    currentPlayer = "0"
else:
    currentPlayer = "X"
board = []
def initaliseBoard():
    for i in range(3):
        row = []
        for i in range(3):
            row.append(' ')
        board.append(row)
def printBoard(board) :
    cell_number = 0
    for row in board:
        for cell in row:
            cell_number += 1
            if cell != ' ':
                print(" " + str(cell) + " ", end="")
            else:
                print(" " + str(cell_number) + " " , end="")
            if (cell_number % 3)  != 0:
                print("|" , end="")
        if cell_number < 9:
            print("\n----------")
    print("\n")
def getPlayerMove(board,currentPlayer) :
    move =  input(currentPlayer , "where do you want to place?(1-9) ")
    if move.isdigit():
        move = int(move)
        move -= 1
        row = move //3
        col = move % 3
        if board[row][col] == " " :
            board[row][col] = currentPlayer
        else:
            print("This spot is taken, take a different one. ")
            getPlayerMove(board)
    else:
        print("Invalid input. Please enter a number.")
        getPlayerMove(board)



## Task 12.3c (get_player_move)
# Modify your 'get_player_move' function to:
# 1. Check if the user's input contains only digits before
#    processing the user's input.
# 2. Else, print "Invalid input. Please enter a number."

## Task 12.3d (get_player_move)
# Modify your 'get_player_move' function to:
# 1. Also check if the user's input is more than or equal to 1
#    and less than or equal to 9
# 2. Else, print "Please enter a number between 1 and 9"

## Task 12.3e (get_player_move)
# Modify your 'get_player_move' function to:
# 1. Check if the chosen cell is empty before assigning 'X' to
#    the cell.
# 2. Else, print "That spot is already taken or invalid. Please
#    choose another."


## Task 12.4a (check_win)
# Create a 'win_conditions' list that holds each of the following
# as a separate item:
# 1. All possible horizontal winning conditions
# 2. All possible vertical winning conditions
# 3. All possible diagonal winning conditions

# There should be 8 items in total.

def check_win(board) :
    win_conditions = [
        [board[0][0],board[0][1],board[0][2]],
        [board[1][0],board[1][1],board[1][2]],
        [board[2][0],board[2][1],board[2][2]],
        [board[0][0],board[1][0],board[2][0]],
        [board[1][0],board[1][1],board[1][2]],
        [board[0][0],board[1][1],board[2][2]],
        [board[0][0],board[1][1],board[2][2]],
        [board[0][2],board[1][1],board[2][0]]
    ]
    for i in win_conditions:
        a,b,c = i
        if (a == b and b == c) and (a != " "):
            return True
    return False
## Task 12.4b (check_win)
# Create a 'check_win' function with 1 parameter, 'board'. This
# function must:
# 1. Contain the 'win_conditions' list you have created earlier
# 2. Loop through each winning condition to check if all 3 cells
#    in the winning condition are the same symbol, and are not
#    spaces (' ').
# 3. Return 'True' if the above condition is met. Else, return
#    'False'


## Task 13.3f (get_player_move)
# Modify your 'get_player_move' function to:
# 1. Take in 1 more parameter, 'current_player'. This parameter
#    will determine the current player ('X' or '0').
# 2. Modify the code to dynamically assign either 'X' or '0' to
#    the board depending on who the current player is.
# 3. Modify the 'print()' function to call for the current player
#    e.g. "Player X, enter your move (1-9): "

# **Main game loop**
# 1. Initiate a new variable 'current_player' and assign it 'X'
# 2. Include 'current_player' as an argument when calling for
#    the 'get_player_move' function
# 3. Test your program by changing 'current_player' between 'X'
#    and '0'


initaliseBoard()
while True:
    printBoard(board)
    getPlayerMove(board,currentPlayer)
    if check_win(board):
        printBoard(board)
        print("YO YOU WON")
        break
