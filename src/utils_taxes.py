import csv

def read_inventory(path_to_inv):
    with open( path_to_inv, newline='') as csv_file:
        logReader = csv.reader(csv_file, delimiter=',')
        inv = {"keys":[]}
        for row in logReader:
            if(row[0] == "price"):
                continue
            inv["keys"].append(row[0])
            inv[row[0]] = row[1]
    print(inv)

read_inventory("../logs/inventory.csv")