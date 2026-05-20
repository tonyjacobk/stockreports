import requests
from pypdf import PdfReader
import re
import requests
import logging
logger = logging.getLogger(__name__)

def download_406_file(url):
    headers = {

          "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    # Use stream=True to handle large files efficiently
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status() # Raise an error for bad status codes
        with open("tempfile", 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def return_text_from_badly_formatted(file_path,num_words):
   try:
        # Create a PdfReader object
    reader = PdfReader(file_path)
    words = []

    for page in reader.pages:
        text = page.extract_text() or ""
        # Normalize whitespace
        text = re.sub(r'(?<=\w)\s(?=\w)', '', text)
        # Extract actual words
        page_words = re.findall(r'\b\w+\b', text)

        remaining = num_words - len(words)
        words.extend(page_words[:remaining])

        if len(words) >= num_words:
            break

    return " ".join(words)
   except FileNotFoundError:
        return f"Error: The file '{file_path}' was not found."
   except Exception as e:
        return f"An error occurred: {e}"
def extract_target_price(text):
    pattern = r"(?i)Target price(.*?)(?=[a-zA-Z]|$)"
    
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        extracted_part = match.group(1)
        # Remove anything that isn't a digit (spaces, special chars)
        numbers_only = re.sub(r'\D', '', extracted_part)
        return numbers_only
    return None

def extract_recommendation(text):
    keywords = ["reccomendation", "recommendation", "rating", "view"]
    reco_list = ["buy", "sell", "reduce", "add"]
    kw_pattern = "|".join(map(re.escape, keywords))
    reco_pattern = "|".join(map(re.escape, reco_list))
    pattern = rf"(?i)\b(?:{kw_pattern})\s*[:\-]?\s*(?<![a-zA-Z])({reco_pattern})"
    match = re.search(pattern, text)
    return match.group(1) if match else None

def get_recomm_target(url):
    download_406_file(url)
    text=return_text_from_badly_formatted("tempfile",200)
    text=text.replace('Valuation Outlook Recommendation',' ')
    first_line = text.splitlines()[0]
    first_line=first_line.lower()
    print("*********************************************",first_line)
    
    tp= extract_target_price(first_line)
    print(tp)
    recomm=extract_recommendation(text)
    print(recomm)
    return tp,recomm
