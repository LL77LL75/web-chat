daily_sales = [1205, 986, 1354, 10535, 15741, 11200, 800, 
               13056, 952, 1100, 1025, 8574, 14014, 9987, 
               1238, 1458, 7803, 900, 13674, 14539, 13241, 
               10886, 7541, 8743, 1482, 11523, 977, 12181, 
               8903, 1008, 1530]
# Example Output/ Answer:
# 5 August has highest sales of $15741
# 7 August has lowest sales of $800
# Average daily sales for August is $6714.71
maximum = max(daily_sales)
minimum = min(daily_sales)
index_num_max = str(daily_sales.index(maximum)+1)
index_num_min = str(daily_sales.index(minimum)+1)
average = round(sum(daily_sales)/len(daily_sales),2)
print(str(index_num_max) + " Agust has the best sales of $" + str(maximum))
print(str(index_num_min) + " Agust has the lowest sales of $" + str(minimum))
print("Average daily sales for August is $" + str(average))