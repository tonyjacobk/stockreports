import re
def remove_quarterlyinfo(text):
    pattern = re.compile(r'\b(?:[1-4]Q|Q[1-4])FY\d{2,4}\b', re.IGNORECASE)
    text = pattern.sub('', text)
    return re.sub(r'\s+', ' ', text).strip()
