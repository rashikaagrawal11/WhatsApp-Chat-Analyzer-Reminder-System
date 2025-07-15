import re
import dateparser

important_keywords = [
    'hackathon', 'summit', 'deadline', 'competition',
    'event', 'exam', 'seminar', 'meeting', 'meet', 'session'
]

# This matches WhatsApp messages like:
# "6/25/25, 9:00 PM - Rashika Agrawal: Message content"
msg_pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}(?:\u202f| )?(?:AM|PM|am|pm)) - (.*?): (.*)'

def extract_keywords_with_time(data):
    extracted = []
    messages = re.findall(msg_pattern, data)

    for date_str, time_str, sender, message in messages:
        lowered = message.lower()

        if any(keyword in lowered for keyword in important_keywords):
            # Combine date and time, parse them
            dt = dateparser.parse(f"{date_str}, {time_str}", settings={'PREFER_DATES_FROM': 'future'})
            keyword = next((kw for kw in important_keywords if kw in lowered), 'Event')

            # Try to find explicit time in message content (in case it's mentioned again)
            time_match = re.search(r'(\d{1,2}:\d{2}(?:\u202f| )?(?:AM|PM|am|pm))', message)
            time_from_msg = time_match.group(1).replace('\u202f', ' ') if time_match else dt.strftime("%I:%M %p")

            extracted.append({
                'keyword': keyword.title(),
                'sender': sender.strip(),
                'message': message.strip(),
                'date': dt.strftime('%Y-%m-%d'),
                'time': time_from_msg
            })

    return extracted
