import os
import time
import requests
import pandas as pd
from typing import List, Dict, Optional
from urllib.parse import unquote
from pathlib import Path
import json
import re
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    print("python-dotenv not installed. Using environment variables directly.")

class GooglePlacesRatingScraper:

    def __init__(self, api_key: str=None):
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
            # MAKE A TRY EXCEPT INCASE OF BAD API KEY
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.session = requests.Session()
    
    def test_api_key(self, place_id_url: str) -> bool:
        endpoint = f"{self.base_url}/details/json"
        place_id = self.extract_place_id(place_id_url) or place_id_url
        params = {
            'place_id': place_id,
            'key': self.api_key
        }

        response = self.session.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        if data['status'] == 'OK':
            print('API key is valid and works!')
            return True
        elif data['status'] == 'REQUEST_DENIED':
            print(f"API key is invalid: {data.get('error_message', 'Unknown error')}")
            return False
        else:
            print(f"API status: {data['status']}")
            return False
    
    def extract_place_id(self, url: str) -> Optional[str]:
        # Pattern for explicit place_id parameter
        match = re.search(r'place_id[=:]([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        # Handles both ChIJ and 0x hex place IDs after !Ns prefix in data= param
        match = re.search(r'!\d+s((?:ChIJ|0x)[a-zA-Z0-9_:%-]+)', url)
        if match:
            return match.group(1)
        return None
    
    def extract_search_query(self, url: str) -> Optional[str]:
        match = re.search(r'[?&]query=([^&]+)', url)
        if match:
            return unquote(match.group(1))
        return None
    
    def find_place_id_by_query(self, query: str) -> Optional[str]:
        endpoint = f"{self.base_url}/findplacefromtext/json"
        params = {
            'input': query,
            'inputtype': 'textquery',
            'fields': 'place_id',
            'key': self.api_key
        }
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            candidates = data.get('candidates', [])
            if candidates:
                return candidates[0]['place_id']
        except Exception:
            pass
        return None
        
    def get_rating(self, identifier:str) -> Dict:
        place_id = self.extract_place_id(identifier)
        if not place_id:
            query = self.extract_search_query(identifier)
            if query:
                place_id = self.find_place_id_by_query(query)
            if not place_id:
                return {
                    'input': identifier,
                    'status': 'error',
                    'error': 'Could not extract or resolve a place ID'
                }
        
        endpoint = f"{self.base_url}/details/json"
        params = {
            'place_id': place_id,
            'fields': 'name,rating,user_ratings_total,formatted_address,website,formatted_phone_number,opening_hours',
            'key': self.api_key
        }

        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            if data['status'] == 'OK':
                result = data['result']
                return {
                    'input': identifier,
                    'place_id': place_id,
                    'name': result.get('name'),
                    'rating': result.get('rating'),
                    'total_ratings': result.get('user_ratings_total'),
                    'address': result.get('formatted_address'),
                    'phone': result.get('formatted_phone_number'),
                    'website': result.get('website'),
                    'status': 'success'
                }
            else:
                return {
                    'input': identifier,
                    'place_id': place_id,
                    'status': 'error',
                    'error': data.get('status', 'Unknown error'),
                    'message': data.get('error_message', '')
                }
        except requests.exceptions.RequestException as exc:
            return {
                'input': identifier,
                'place_id': place_id,
                'status': 'error',
                'error': str(exc)
            }
        
    def scrape_batch(self, businesses: List[str], delay: float = 0.1) -> pd.DataFrame:
        results = []
        total = len(businesses)

        for i, business in enumerate(businesses, 1):
            print(f"Processing {i}/{total}: {business:100}...")

            result = self.get_rating(business)
            results.append(result)

            if i < total:
                time.sleep(delay)
        return pd.DataFrame(results)
    
    def save_results(self, df:pd.DataFrame, ratings_filename: str = 'company_ratings.csv', summary_filename: str = 'summary.json'):
        df.to_csv(ratings_filename, index=False)
        print(f"\nResuls saved to {ratings_filename}")
        successful = df[df['status'] == 'success']
        if not successful.empty:
            print("\nSummary Stats:")
            print(f"    Total Businesses: {len(df)}")
            print(f"    Successful: {len(successful)}")
            print(f"    Failed: {len(df) - len(successful)}")
            print(f"    Total Reviews: {successful['total_ratings'].sum():,}")

            summary = {
                'total_processed': len(df),
                'successful': len(successful),
                'failed': len(df) - len(successful),
                'total_reviews': successful['total_ratings'].sum()
            }

            with open(summary_filename, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"    Summary saved to {summary_filename}")




