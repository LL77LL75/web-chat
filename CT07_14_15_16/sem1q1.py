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
max(daily_sales)
print(str(daily_sales.index(maximum)) + " Agust has the best sales of $" + str(max(daily_sales)))