import json
from datetime import datetime

# Path to the JSON file
file_path = 'updated_video_data.json'

# Load the JSON data
with open(file_path, 'r') as f:
    data = json.load(f)

# Update the upload_date format for each entry
for entry in data:
    date_obj = datetime.strptime(entry['upload_date'], '%Y%m%d')
    entry['upload_date'] = date_obj.strftime('%d-%m-%Y')

# Write the updated data back to the file
with open('video_data_v2.json', 'w') as f:
    json.dump(data, f, indent=4)

print("Upload dates have been updated.")