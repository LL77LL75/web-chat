# # if 0 == 1:

#     # # i = 1
#     # # while True:
#     # #     print(i)
#     # #     i+=1
#     # # savings = 0
#     # # while savings <100:
#     # #     savings += int(input("how much did you save today? "))
#     # # else:
#     # #     print("you saved $100 or more!")
#     # import random
#     # lives = 3
#     # questions = 15
#     # a = random.randint(2,20)
#     # b = random.randint(2,20)
#     # ans = 0
#     # while not(questions<1):
#     #     if int(input("what is " + str(a)+ " * " +str(b) +" ")) == a*b:
#     #         a = random.randint(2,20)
#     #         b = random.randint(2,20)
#     #         questions-=1
#     #     else:
#     #         lives-=1
#     #     if lives<1:
#     #         print("GO TO REMEDIAL FOR 100,000 YEARS")
#     #         break
#     # else:
#     #     print("you did well")
#     # planets = ["mercury","venus","earth","mars","jupiter","saturn","uranus","neptune"]
#     # planets.insert(3,"aaaaa")
#     # print(planets)
#     # for i in planets:
#     #     if i == "earth":
#     #         print(i + " : this is my home")
#     #     elif i == "mars":
#     #         print(i + " : I CONQUERED THIS")
#     #     elif i == "aaaaa":
#     #         print(i + " : I CREATED THIS")
#     #     else:
#     #         print(i)
#     print()
food = []
if input("password ") == "blank":
    ans = input("what food would you like? ")
    while ans != "end":
        if ans !=" ":
            food.append(ans)
        ans = input("what food would you like? ")
    for i in food:
        word = i[0].upper() + i[1:len(i)]
        i = word
a = input("what would you like? ")

for i in food:
    if a == i :
        print("yes, we sell that.Please have a seat.")
        break
    if i == food[len(food)-1]:
        print("sorry, please go next door")