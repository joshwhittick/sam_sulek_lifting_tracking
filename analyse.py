import json
import re
from datetime import datetime
import json
import pandas as pd
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

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
            lift = lift.replace(' and ', ';')
            lift = lift.replace(',', ';')
            lift = lift.replace('; ', ';')
            lift = lift.replace(' ;', ';')

            lifts = lift.split(';')
            lifts = sorted(lifts, key=lambda x: x.strip())
            lift = ';'.join(lifts)

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

def get_current_stats(new_data):
    event_set = set()
    day_set = set()
    lift_set = set()
    overall_lift_set = set()

    event_dates = {}

    for day in new_data:
        if day['day'] != 'None':
            day_set.add(day['day'])
        if day['event'] != 'None':
            event_set.add(day['event'])
        if day['lift'] != 'None':
            lift_set.add(day['lift'])
            lifts = day['lift'].split(';')
            for lift in lifts:
                overall_lift_set.add(lift.strip())

        if day['event'] != 'None':
            date_str = day['upload_date']
            try:
                date = datetime.strptime(date_str, '%d-%m-%Y')
            except ValueError:
                continue

            if day['event'] not in event_dates:
                event_dates[day['event']] = []
            event_dates[day['event']].append(date)

    # Sort alphabetically
    overall_lift_set = sorted(overall_lift_set)

    overall_lift_ocurences = {}
    for lift in overall_lift_set:
        count = 0
        for x in new_data:
            if lift in x['lift']:
                count += 1
        overall_lift_ocurences[lift] = count


    event_set = sorted(event_set)
    day_set = sorted(day_set)
    lift_set = sorted(lift_set)

    event_lengths = {}
    event_start_end = {}

    for event in event_set:
        highest_val = 0
        for x in new_data:
            if x['event'] == event and x['day'] != 'None':
                try:
                    day_val = int(x['day'])
                    if day_val > highest_val:
                        highest_val = day_val
                except ValueError:
                    continue
        event_lengths[event] = highest_val

        if event in event_dates:
            sorted_dates = sorted(event_dates[event])
            event_start_end[event] = (sorted_dates[0], sorted_dates[-1])

    lift_ocurences = {}
    for lift in lift_set:
        count = 0
        for x in new_data:
            if x['lift'] == lift:
                count += 1
        lift_ocurences[lift] = count

    lift_ocurences = dict(sorted(lift_ocurences.items(), key=lambda item: item[1], reverse=True))
    event_lengths = dict(sorted(event_lengths.items(), key=lambda item: item[1], reverse=True))



    return event_set, day_set, lift_set, event_lengths, lift_ocurences, event_start_end, overall_lift_ocurences