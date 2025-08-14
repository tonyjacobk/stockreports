from pypdf import PdfReader
import re
import requests
def download_file(url):
 try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        with open("tempfile", 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

 except requests.exceptions.RequestException as e:
       raise e 
  
def find_rating_from_file():
 reader = PdfReader("tempfile")
 page = reader.pages[0]  # Access the first page
 text = page.extract_text()

 match = re.search(r'Rating:\s*(\w+)', text)

    # Return the matched word if found, otherwise return None
 return match.group(1) if match else None



def get_target_price_from_file():
 reader = PdfReader("tempfile")
 page = reader.pages[0]  # Access the first page
 text = page.extract_text()
 print(text)
 pattern = re.compile(
                r'target price[^\d]*([\d,]+(?:\.\d+)?|[\d.]+(?:,\d+)?)', 
                re.IGNORECASE
            )
            
 match = pattern.search(text)
            
 if match:
                # Get the matched number string and clean it
  num_str = match.group(1)
                
                # Handle thousand separators and decimal points
  if ',' in num_str and '.' in num_str:
                    # Assume commas are thousand separators and . is decimal
                    num_str = num_str.replace(',', '')
  elif ',' in num_str:
                    # Check if comma is used as decimal separator (European style)
                    if num_str.count(',') == 1 and len(num_str.split(',')[1]) <= 2:
                        num_str = num_str.replace(',', '.')
                    else:
                        num_str = num_str.replace(',', '')
  return(num_str)              
                # Convert to appropriate numeric type
 return " "
def get_target_price(url):
 value=" "
 try:
  download_file(url)
  value=get_target_price_from_file()
 except Exception as e:
  pass
 return (value)

def get_recommendation(url):
 value=" "
 try:
  download_file(url)
  value=find_rating_from_file()
 except Exception as e:
  pass
 return (value)

def get_recomm_and_target(url):
 print(url)
 value=" "
 recomm=" "
 try:
  download_file(url)
  recomm=find_rating_from_file()
  value=get_target_price_from_file()
  print ("recommendation ",recomm," Target ",value)
 except Exception as e:
  print("Could not get from :",url)
  print(str(e))
 print (value,recomm)
 return value ,recomm

