list = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',' ',',','.']
i=0
def binary(num):
    return bin(num)[2:]
    binary_string = binary(num)
def num(binary_item):
    binary_str = str(binary_item)
    return int(binary_item, 2)

message = input("Enter a message: ")
import random
def heck(num):
    binary_str = bin(num)[2:] 
    numbers = []
    i = 0
    while i < len(binary_str):
        group_size = random.choice([2, 3])
        group = binary_str[i:i+group_size]
        if len(group) < group_size:
            group += "0" * (group_size - len(group))
        numbers.append(int(group, 2))
        i += group_size
    return numbers
def unheck(num):
    binary_str = ""
    for number in num:
        binary_str += bin(number)[2:]
    return int(binary_str, 2)    
