import os
from dotenv import load_dotenv
import pandas as pd
from places_rating_scraper import GooglePlacesRatingScraper
import numpy

if __name__ == "__main__":
    load_dotenv()
    try:
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        scraper = GooglePlacesRatingScraper(api_key)

        if not scraper.test_api_key("https://www.google.com/maps/place/Accessibility+Specialists-Fl/data=!4m2!3m1!19sChIJdxLkibbL5YgRiimQ-5nAblY"):
            print("\n   API key failed.")
            exit(1)
        
        print("\n")
        print("SCRAPING")

        df = pd.read_csv('Jacksonville-Eye-Spy-DB.csv')
        if 'google_map_url' not in df:
            print("ERROR: csv file not in correct format.")
            exit(1)
        if 'updated_map_url' in df:
            df = df[['google_map_url', 'updated_map_url']]
            df['updated_map_url'] = df['updated_map_url'].combine_first(df['google_map_url'])
            link_list = df['updated_map_url'].tolist()
        else:
            link_list = df['google_map_url'].tolist()
        results = scraper.scrape_batch(link_list)
        scraper.save_results(results)
        
    except ValueError as e:
        print(f"Configuration error: {e}")
    
    except Exception as e:
        print(f"Other error: {e}")
