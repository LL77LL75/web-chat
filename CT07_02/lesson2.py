# if 1 == 3:
#     SCORe = 0
#     answer1 = input("how many legs does an octopus have? ")
#     a = 1
#     # while 1>0:
#     #     a = a+1
#     #     print(a)
#     while (answer1 != "8") and not(answer1 == "skip"):
#         answer1 = input("how many legs does an octopus have? ")
#     else:
#         if answer1 != "skip":
#             SCORe+=1
#         answer2 = input("how many months are there in a year? ")
#         while (answer2 != "12") and not(answer2 == "skip"):
#             answer2 = input("how many months are there in a year? ")
#         else:
#             if answer2 != "skip":
#                 SCORe+=1
#             answer3 = input("how letters are there in the alpabet? ")
#             while (answer3 != "26") and not(answer3 == "skip"):
#                 answer3 = input("how letters are there in the alpabet? ")
#     if answer3 != "skip":
#         SCORe+=1
#     print("u have at least 1 iq")
#     print("your score is " + str(SCORe))
#     # answer1 = input("what comes once in a minute twice in a moment but never in a thousand years? ")
#     # while answer1 !="the letter m":
#     #     answer1 = input("what comes once in a minute twice in a moment but never in a thousand years? ")
import time
study = int(input("how many minutes do you want to study? "))
while 0.0< study:
    time.sleep(60)
    study-=1.0
    print(study)
print("∞ minutes to go")