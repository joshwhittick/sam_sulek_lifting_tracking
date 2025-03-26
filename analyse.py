import json
import re

file = open('video_dict_3.json', 'r')
data = json.load(file)
file.close()

regex_1 = r"^(.+?) Day (\d+) - (.+) (?=-)- (.+)"
regex_2 = r"^(.+?) [dD]ay (\d+)(?: Part \d)? - ([a-zA-Z \.\,\/]+)"

new_data = []

for day in data:
    title = day['title']
    match_1 = re.match(regex_1, title)
    match_2 = re.match(regex_2, title)

    if match_1:
        event = match_2.group(1).strip()
        day_number = match_2.group(2).strip()
        lift = match_2.group(3).strip()

    elif match_2:
        event = match_2.group(1).strip()
        day_number = match_2.group(2).strip()
        lift = match_2.group(3).strip()
    
    if match_1 or match_2:
        print(f"Event: {event}, Day: {day_number}, Lift: {lift}")
        
        new_data.append({
            'event': event,
            'day': day_number,
            'lift': lift
        })
    
print(len(data))
print(len(new_data))