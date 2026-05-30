import json
import re
from datetime import datetime

from muscle_parser import parse_title

# Canonical lifting-phase names. Maps the raw phase text found in a title to its
# canonical event. New phases not listed here are kept verbatim.
PHASE_DICT = {
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
    'Spring Bulk': 'Spring Bulk',
    'Cutzilla': 'Cutzilla',
    'Cuzilla': 'Cutzilla',  # typo fix in source titles
    'The Bulk Awakens': 'The Bulk Awakens',
    'Bulk': 'The Bulk Awakens',  # 'Bulk Day 10-25' continues 'The Bulk Awakens Day 1-9'
    'Diet': 'Cutzilla',          # 'Diet Day 1' is Cutzilla day 1 (titled before the name was set)
    'Italy': 'Italy',
}

# Recognised lifting phases. Used when validating manually-curated events on
# videos whose title carries no 'Day N' (e.g. trip/announcement videos), so that
# stray one-off labels from the old parser are dropped rather than shown as
# phases. New phases that appear with day numbers are captured automatically and
# do not need to be listed here.
VALID_EVENTS = {
    'Spring Bulk', 'Winter Bulk', 'Fall Cut', 'Spring Cut', 'The Bulk',
    'Offseason', 'Winter Shredathon', 'Cutzilla', 'The Bulk Awakens', 'Italy',
}

_DAY_RE = re.compile(r'\b[Dd]ay\s+(\d+)')


def parse_event_day(title):
    """Extract (event, day) from a title.

    Handles both orderings: forward 'Phase Day N - <lift>' and reversed
    '<lift> - Phase Day N'. The event is the text segment immediately before
    'Day N' (after the last ' - ' if present), normalised via PHASE_DICT.
    Returns ('None', 'None') when there is no day marker.
    """
    m = _DAY_RE.search(title)
    if not m:
        return 'None', 'None'

    day_number = m.group(1)
    before = title[:m.start()].strip()
    candidate = before.split(' - ')[-1].strip() if ' - ' in before else before
    candidate = ' '.join(candidate.split())
    event = PHASE_DICT.get(candidate, candidate) if candidate else 'None'
    return event, day_number


def clean_and_enrich_json(json_dict):
    """Clean titles and derive event, day, lift and muscle_group for each video.

    Lifts are extracted by scanning the whole title for muscle keywords
    (see muscle_parser), not by positional slots, so creative titles and either
    title ordering are handled. Manual judgement calls live in
    manual_overrides.json and are applied by parse_title.
    """
    new_data = []

    for day in json_dict:
        title = ' '.join(day['title'].split())  # strip + collapse internal whitespace
        day['title'] = title

        event, day_number = parse_event_day(title)
        parsed = parse_title(title)

        new_data.append({
            'title': title,
            'video_url': day['video_url'],
            'upload_date': day.get('upload_date', ''),
            'event': event,
            'day': day_number,
            'lift': parsed['lift'],
            'muscle_group': parsed['muscle_group'],
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