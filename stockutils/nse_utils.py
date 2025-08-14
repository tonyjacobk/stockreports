import requests
from typing import Tuple,List,Dict,Optional
class NSEClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        })
    def get_companies(self, query: str) ->Tuple[ int,dict]:

        url = "https://www.nseindia.com/api/NextApi/search/autocomplete"
        params = {"q": query}
        print ("Checking ...",query)
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            symbols = result.get("symbols", [])
            return symbols
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return -1,None
        except ValueError:
            print("Invalid JSON received")
            return -1,None

nse=NSEClient()
