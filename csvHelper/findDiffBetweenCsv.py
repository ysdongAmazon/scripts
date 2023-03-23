import csv

csv.field_size_limit(1000000000) # set the field size limit to 1GB to avoid memory error

# Read in the first CSV file
with open('file1.csv', 'r') as f2:
    reader2 = csv.DictReader(f2)
    file2_accounts = set(row['AccountID'] for row in reader2)

# Read in the second CSV file
with open('unique_accounts7.csv', 'r') as f1:
    reader1 = csv.DictReader(f1)
    file1_accounts = set(row['accountId'] for row in reader1)

# count the accounts in file1 and file2
print(f"Accounts in file1: {len(file1_accounts)}")
print(f"Accounts in file2: {len(file2_accounts)}")

# Find the accounts that are in file1 but not in file2
diff_accounts = file2_accounts - file1_accounts

# Print the accounts that are in file1 but not in file2
print(f"Accounts in file1 but not in file2: {', '.join(diff_accounts)}")

