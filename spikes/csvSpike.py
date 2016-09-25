import csv

with open('test.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
    for i in range(5):
        writer.writerow({"key":"value"})