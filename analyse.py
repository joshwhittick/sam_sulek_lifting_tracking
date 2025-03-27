import json
import re

def clean_and_enrich_json(json_dict):
    new_data = []
    regex_1 = r"^(.+?) Day (\d+) - (.+) (?=-)- (.+)"
    regex_2 = r"^(.+?) [dD]ay (\d+)(?: Part \d)? - ([a-zA-Z \.\,\/]+)"

    lifts_data = json.load(open('lift_types.json', 'r'))
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

    for day in json_dict:
        title = day['title']
        title = title.strip()
        title = title.replace('  ', ' ')
        title = title.replace('Arms, ', 'Arms - ')
        title = title.replace('WI', 'Wi')
        day['title'] = title

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

            event = event.replace('  ', ' ')
            event = phase_dict.get(event, event)

            lift = lifts_data.get(lift, lift)

            new_data.append({
                'title': day['title'],
                'video_url': day['video_url'],
                'upload_date': day['upload_date'],
                'event': event.strip(),
                'day': day_number.strip(),
                'lift': lift.strip()
            })
        
        else:
            new_data.append({
                'title': day['title'],
                'video_url': day['video_url'],
                'upload_date': day['upload_date'],
                'event': 'None',
                'day': 'None',
                'lift': 'None'
            }) 

    return new_data

data = json.load(open('video_data_final.json', 'r'))
new_data = clean_and_enrich_json(data)

#print(json.dumps(new_data, indent=4))


def get_current_stats(new_data):
    event_set = set()
    day_set = set()
    lift_set = set()

    for day in new_data:
        if day['day'] != 'None':
            day_set.add(day['day'])
        if day['event'] != 'None':
            event_set.add(day['event'])
        if day['lift'] != 'None':
            lift_set.add(day['lift'])

    event_set = sorted(event_set)
    day_set = sorted(day_set)   
    lift_set = sorted(lift_set)

    event_lengths = {}
    for event in event_set:
        highest_val = 0
        for x in new_data:
            if x['event'] == event:
                day_val = x['day']
                if day_val == 'None':
                    continue
                day_val = int(day_val)
                if day_val > highest_val:
                    highest_val = day_val
        event_lengths[event] = highest_val

    lift_ocurences = {}
    for lift in lift_set:
        count = 0
        for x in new_data:
            if x['lift'] == lift:
                count += 1
        lift_ocurences[lift] = count

    lift_ocurences = dict(sorted(lift_ocurences.items(), key=lambda item: item[1], reverse=True))
    event_lengths = dict(sorted(event_lengths.items(), key=lambda item: item[1], reverse=True))

    return event_set, day_set, lift_set, event_lengths, lift_ocurences