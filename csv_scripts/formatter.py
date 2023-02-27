import csv
import json

csv_file = 'output.csv'
json_file = 'restaurant_data.json'

# Open CSV file and read data
with open(csv_file, mode='r') as file:
    csv_reader = csv.DictReader(file)
    data = []
    
    for row in csv_reader:
        print(row)
        data.append({'id': row['ID'], 'cuisine': row['category']})

# Write data to JSON file
with open(json_file, mode='w') as file:
    for i, row in enumerate(data):
        # Create index and document ID for Elasticsearch
        index = {"index": {"_index": "restaurants", "_id": i+1}}
        # Write data to JSON file
        json.dump(index, file)
        file.write('\n')
        json.dump(row, file)
        file.write('\n')
