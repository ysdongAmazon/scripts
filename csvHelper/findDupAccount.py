import csv
from collections import Counter

# Replace 'file.csv' with your CSV file name
filename = 'unique_accounts_3.csv'

# Replace 'accountId' with the column name for the account IDs in your CSV file
account_id_column = 'accountId'

account_ids = []

with open(filename, mode='r') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    
    for row in csv_reader:
        account_id = row[account_id_column]
        account_ids.append(account_id)

counter = Counter(account_ids)

# Print duplicate account IDs
for account_id, count in counter.items():
    if count > 1:
        print(f'Duplicate account ID: {account_id} (Count: {count})')