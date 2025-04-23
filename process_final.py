import json

file = 'video_data_final.json'

# Safely open and load the JSON data
with open(file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Process each day's lift string
for day in data:
    if 'lift' in day and isinstance(day['lift'], str):
        lifts = [lift.strip() for lift in day['lift'].split(';') if lift.strip()]
        lifts = sorted(lifts)
        day['lift'] = ';'.join(lifts)

# Save the updated data back to the file
with open(file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)