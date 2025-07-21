import requests
from bs4 import BeautifulSoup
import logging
logger = logging.getLogger(__name__)


def get_moneycontrol_article_content(url):
    """
    Fetches the content of a Moneycontrol article using Beautiful Soup.

    Args:
        url (str): The URL of the Moneycontrol article.

    Returns:
        bs4.BeautifulSoup object: A Beautiful Soup object representing the parsed HTML,
                                 or None if there was an error.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()

        # Parse the HTML content using Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_pdf(soup):
    related_block = soup.find('div', class_='related_stories_left_block')

    if related_block:
    # 2. Initialize a counter for paragraphs
     p_count = 0
     second_p = None

    # 3. Iterate through subsequent siblings
    # .next_siblings includes text nodes, so we filter for tags
     for sibling in related_block.next_siblings:
        if sibling.name == 'p': # Check if the sibling is a <p> tag
            p_count += 1
            if p_count == 2:
                second_p = sibling
                break # Found the second <p>, so we can stop

     if second_p:
        print(f"Found the second <p> after 'related_stories_left_block':\n'{second_p.get_text(strip=True)}'")
        anchor_tag = second_p.find('a')
        if anchor_tag:
                href_value = anchor_tag.get('href')
                print(f"Found href inside the second <p>: {href_value}")
                return (href_value)
        else:
                print("No <a> tag found inside the second <p>.")
     else:
        print("Could not find the second <p> after 'related_stories_left_block'.")
    else:
      print("Element with class 'related_stories_left_block' not found.")
    return None 
    

def get_real_url(url):
# Get the Beautiful Soup object
  soup = get_moneycontrol_article_content(url)
  nurl=None
  if soup:
    logger.info("Successfully parsed the page %s . ",url)
    nurl= get_pdf(soup) 
  else:
    logger.error("Failed to get or parse the webpage. %s",url)
  if not nurl :
    nurl=url
  return (nurl)  
