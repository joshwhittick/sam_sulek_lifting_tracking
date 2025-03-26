import json
import re

file = open('main_data.json', 'r')
data = json.load(file)
file.close()

lifts_file = open('lift_types.json', 'r')
lifts_data = json.load(lifts_file)
lifts_file.close()

regex_1 = r"^(.+?) Day (\d+) - (.+) (?=-)- (.+)"
regex_2 = r"^(.+?) [dD]ay (\d+)(?: Part \d)? - ([a-zA-Z \.\,\/]+)"

new_data = []

phase_dict = {
    'Winter Bulk': 'Winter Bulk',
    'Fall Cut': 'Fall Cut',
    'Spring Cut': 'Spring Cut',
    'Spring Cut Finale': 'Spring Cut',
    'End of Fall Cut': 'Fall Cut',
    'The Bulk': 'The Bulk',
    'Offseason': 'Offseason',
    'Winter Shredathon (Name TBD)': 'Winter Shredathon',
    'Winter Shredathon': 'Winter Shredathon',
    'Clothing Announcement - Winter Shredathon': 'Winter Shredathon',
    'Spring Bulk': 'Spring Bulk'
}

for day in data:
    title = day['title']
    title = title.strip()
    title = title.replace('  ', ' ')
    title = title.replace('Arms, ', 'Arms - ')
    title = title.replace('WI', 'Wi')
    day['title'] = title

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
        new_data.append({
            'title': day['title'],
            'vide_url': day['url'],
            'event': event.strip(),
            'day': day_number.strip(),
            'lift': lift.strip()
        })
    
    else:
        #print(f"{title}")
        x = 0

for day in new_data:
    event = day['event']
    event = event.replace('  ', ' ')
    event = phase_dict.get(event, event)
    day['event'] = event

    lift = day['lift']
    lift = lifts_data.get(lift, lift)
    day['lift'] = lift

event_set = set()
day_set = set()
lift_set = set()

for day in new_data:
    event_set.add(day['event'])
    day_set.add(day['day'])
    lift_set.add(day['lift'])

"""print('\n')
print(list(event_set))
print(len(event_set))"""

#sort alphabetically
event_set = sorted(event_set)
day_set = sorted(day_set)   
lift_set = sorted(lift_set)

for x in lift_set:
    print(x)