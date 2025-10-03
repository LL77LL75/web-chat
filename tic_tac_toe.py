import random
import os

MOVES_FILE = "moves.txt"

def load_moves():
    """Load moves from file into a list of ints."""
    if not os.path.exists(MOVES_FILE):
        return []
    with open(MOVES_FILE, "r") as f:
        return [int(line.strip()) for line in f if line.strip().isdigit()]

def save_moves(moves):
    """Save moves list back to file."""
    with open(MOVES_FILE, "w") as f:
        for move in moves:
            f.write(f"{move}\n")

def print_board(board):
    """Pretty-print the board."""
    for i in range(0, 9, 3):
        print(" ".join(board[i:i+3]))
    print()

def check_win(board, symbol):
    """Check if given symbol has won."""
    wins = [
        (0,1,2),(3,4,5),(6,7,8),  # rows
        (0,3,6),(1,4,7),(2,5,8),  # cols
        (0,4,8),(2,4,6)           # diagonals
    ]
    return any(all(board[i] == symbol for i in combo) for combo in wins)

def ai_move(board, moves):
    """AI chooses move based on moves.txt file."""
    tried = set()
    while True:
        if not moves:  # if file empty, choose any random
            move = random.randint(1, 9)
        else:
            move = random.choice(moves)
        if move in tried:  # already tried this invalid move
            if len(tried) == 9:  # no moves left
                return None
            continue
        if board[move-1] == " ":
            return move
        else:
            tried.add(move)

def main():
    moves = load_moves()
    board = [" "] * 9
    ai_moves_this_game = []

    print("Tic-Tac-Toe")
    print_board([str(i+1) for i in range(9)])

    current = "X"  # player always X, AI always O

    while True:
        if current == "X":
            # Human move
            move = None
            while move is None:
                try:
                    choice = int(input("Your move (1-9): "))
                    if 1 <= choice <= 9 and board[choice-1] == " ":
                        move = choice
                    else:
                        print("Invalid move. Try again.")
                except ValueError:
                    print("Enter a number 1-9.")
            board[move-1] = "X"
        else:
            # AI move
            move = ai_move(board, moves)
            if move is None:
                print("No moves left.")
                break
            board[move-1] = "O"
            ai_moves_this_game.append(move)
            print(f"AI plays {move}")

        print_board(board)

        # Check win
        if check_win(board, current):
            if current == "X":
                print("You win!")
                # Remove AI moves from file
                moves = [m for m in moves if m not in ai_moves_this_game]
                save_moves(moves)
            else:
                print("AI wins!")
                # Add final move 3 times
                moves.extend([move] * 3)
                save_moves(moves)
            break

        # Check draw
        if " " not in board:
            print("It's a draw!")
            break

        # Switch turns
        current = "O" if current == "X" else "X"

if __name__ == "__main__":
    main()
