import turtle
t = turtle.Turtle()
window = turtle.Screen()
window.setup(800,400)
window.bgcolor("forestgreen")
t.shape('square')
# t.seth(0)
# sides = int(input("sides "))
# t.pendown()
# for i in range(sides):
#     t.forward(100)
#     t.left(360/sides)
t.penup()
t.sety(250)
t.setx(-400)
t.pendown()
while t.xcor() < 400:
    t.penup()
    t.setx(t.xcor()- 25)
    t.pendown()
    t.stamp()


# **Task 1b**: Drawing the finish line
# Adding on to your previous answer, create a line of black
# squares at y = 250 by creating a black square turtle object
# and stamping it from  to x = 300 at 25 pixel-
# intervals

# 1. Create a turtle object named 'pen'
# 2. Lift the pen up
# 3. Using '.shape()', set the turtle object's shape to "square"
# 4. Using '.sety()', set turtle object's y position to 250
# 5. Using a 'for i in range()' loop, use the 'i' variable to
#    create a stamp of 'pen' turtle object from x = -300 to
#    x = 300 at 25-pixel intervals:
#         a. Set 'pen' turtle's x coordinate using '.setx()'
#         b. Stamp a copy of 'pen' turtle at its current
#            position using '.stamp()'

# Tip: Use '.mainloop()' at the end of your program to keep the
# window open

# You should see this when you run the program! (Refer to slides)


# **Task 1c**: Drawing the start line
# Adding on to your previous answer, use the 'pen' turtle object
# you have created earlier to draw a horizontal yellow start
# line at y = -250.

# 1. Using '.goto()', set 'pen' turtle's coordinates to
#    (-300, -250)
# 2. Using the following commands, set the colour of 'pen' to
#    "yellow", set heading to 0 and move forward by 600
#    before hiding the turtle:
#         a. '.pencolor()'
#         b. '.pendown()'
#         c. '.seth()'
#         d. '.forward()'
#         e. '.hideturtle()'

# Tip: Use '.mainloop()' at the end of your program to keep the
# window open

# You should see this when you run the program! (Refer to slides)







window.mainloop()