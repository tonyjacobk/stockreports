import os
import re
from pypdf import PdfReader
from typing import List, Dict, Any

def extract_text_from_pdf(file_path, num_words=2000):
  try:
        # Create a PdfReader object
        reader = PdfReader(file_path)
        full_text = ""

        # Iterate through all pages to get the full text
        for page in reader.pages:
            full_text += page.extract_text()

            # If we've already extracted enough text, we can stop
            # and process what we have.
            if len(full_text.split()) >= num_words:
                break

        # Split the full text into a list of words
        words = full_text.split()

        # Take only the first `num_words` from the list
        first_n_words = " ".join(words[:num_words])

        return first_n_words
  except FileNotFoundError:
        return f"Error: The file '{file_path}' was not found."
  except Exception as e:
        return f"An error occurred: {e}"

def extract_meta_data(file_path):
  try:
   reader = PdfReader(file_path)
   meta = reader.metadata
   return meta
  except exception as e:
   return None



def extract_context(text: str, window_size: int = 10) -> List[Dict[str, Any]]:
    """
    Searches the text for target keywords ('Target Price', 'TP', 'recommend')
    and extracts a context window of words before and after each occurrence.

    Args:
        text: The input string (e.g., an analyst report).
        window_size: The number of words to extract before and after the keyword.

    Returns:
        A list of dictionaries, each containing the found keyword and the
        extracted context snippet.
    """
    # Split the text into a list of words using whitespace as a delimiter.
    # This keeps surrounding punctuation attached to the words (e.g., 'stock.')
    # which provides better context in the output snippet.
    words = re.split(r'\s+', text.strip())

    if not words or words == ['']:
        return []

    results = []
    i = 0

    # Iterate through the list of words
    while i < len(words):
        # Normalize the word by converting to lowercase and stripping common punctuation
        # for robust matching, but keep the original word in 'words' for the output.
        normalized_word = words[i].lower().strip(',.?!-:"\'()[]{}')
        keyword = None
        keyword_length = 1

        # 1. Check for single-word matches ('TP', 'recommend')
        if normalized_word == 'tp' or normalized_word == 'recommend':
            # Use the original word(s) for the output
            keyword = words[i]
            keyword_length = 1

        # 2. Check for multi-word match ('Target Price')
        elif normalized_word == 'target':
            if i + 1 < len(words):
                normalized_next_word = words[i+1].lower().strip(',.?!-:"\'()[]{}')
                if normalized_next_word == 'price':
                    keyword = f"{words[i]} {words[i+1]}"
                    keyword_length = 2

        if keyword:
            # --- Match Found ---

            # Determine the context window boundaries
            # Start index: Ensure it doesn't go below the list's start (0)
            start_index = max(0, i - window_size)

            # End index: Ensure it doesn't exceed the list's end (len(words))
            # The keyword ends at index (i + keyword_length - 1). We look 
            # 'window_size' words *after* the keyword finishes.
            end_index = min(len(words), i + keyword_length + window_size)

            # Extract the snippet and join it back into a readable string
            snippet_words = words[start_index:end_index]
            snippet_text = ' '.join(snippet_words)

            results.append({
                'keyword_match': keyword,
                'context_snippet': snippet_text,
                'start_index': start_index,
                'end_index': end_index - 1
            })

            # Advance the iterator past the entire keyword (1 for 'TP', 2 for 'Target Price')
            i += keyword_length
        else:
            i += 1

    return results

def extract_needed_texts(fname):
 text=extract_text_from_pdf(fname)
 texts=extract_context(text)
 ftexts=""
 for i in texts:
  ftexts=ftexts+" " + i['context_snippet']
 return (ftexts)
