## Task 1: Function without parameter (w/o turtle)
# You are required to print the same "Motion Detected" phrase
# multiple times as part of a motion detecting program that you
# are creating.

# Create an 'alert()' function that will print "Motion Detected"
# whenever the function is called.

# **Example**
# Input:
#     alert()
# Output:
#     Motion Detected
def alert():
    print('motion detected ' * 100000)
alert()

## Task 2: Function without parameter (w turtle)
# Using the 'turtle' library, create a 'square()' function that
# draws a 20x20 square at the turtle object's current position
# whenever the function is called.

# By calling the 'square()' function, draw a square anywhere
# within the turtle window.
import turtle
t = turtle.Turtle()
window = turtle.Screen()
window.setup(800, 400)
def square1():
    for i in range(4):
        t.forward(40)
        t.right(90)
square1()


## Task 3: Function with parameter (w/o turtle)
# Write a Python function 'multiply()', that takes 2 parameters,
# a and b, and prints the product of these 2 numbers.

# **Example**
# Input:
#     multiply(3,5)
# Output:
#     15

## Task 4: Function with parameter (w turtle)
# Using the 'turtle' library, create a function 'drawSquare()',
# with 2 parameters, x and y, and draw a 20x20 square at the
# coordinate (x, y).

# You may use the following steps as a guide:
# 1. Import 'turtle' library
# 2. Create a turtle object using 'turtle.Turtle()'
# 3. Define a function 'drawSqare()' with 2 parameters, x and y
#         a. Lift the pen using '.penup()'
#         b. Reposition the turtle object using '.goto(x, y)'
#         c. Put the pen down using '.pendown()'
#         d. Create a 'for' loop to draw a square
# 4. Test out your program using 'drawSquare(-50, 50)'
# 5. Use '.mainloop()' to keep the window open
def square(x,y):
    t.goto(x,y)
    for i in range(4):
        t.forward(40)
        t.right(90)
s