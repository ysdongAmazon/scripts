
import csv

def read_and_sort_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        rows = sorted(reader)
    return header, rows

def compare_csv_files(file1, file2):
    header1, rows1 = read_and_sort_csv(file1)
    header2, rows2 = read_and_sort_csv(file2)

    return header1 == header2 and rows1 == rows2

file1 = 'unique_accounts6.csv'
file2 = 'unique_accounts7.csv'

if compare_csv_files(file1, file2):
    print("The CSV files are the same.")
else:
    print("The CSV files are different.")