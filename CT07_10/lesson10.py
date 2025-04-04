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
# def square1():
#     for i in range(4):
#         t.forward(40)
#         t.right(90)
# square1()


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
# def square(x,y):
#     t.goto(x,y)
#     for i in range(4):
#         t.forward(40)
#         t.right(90)
# square(100,100)


## Task 5: Function with return value (w/o turtle)
# Define an 'isElderly()' function with 1 parameter, age,
# and return True if the age is larger than, or equal to 65.

# Using the 'isElderly()' function created, create a program
# that asks the user for their age. Then use an 'if' statement
# to print "You are eligible for an elderly discount" if
# 'isElderly()' returns True.

# def isElderly(age):
#     return age >= 65
# if isElderly(int(input("age"))):
#     print("u get discount")
# else:
#     print("no discount for u")

## Task 6: Function with return value (w turtle)
# Using 'xcor()' and 'ycor()', create a function 'turtleCoord()'
# that takes in a parameter, turtle_obj, and returns the current
# x and y coordinates of the turtle object.

# Then, using the 'turtleCoord()' function, modify your answer
# from Task 4 to print out the coordinates of the turtle object
# after drawing a square.
def turtleCoord(turtle):
    return [turtle.xcor(),turtle.ycor()]
turtleCoord 