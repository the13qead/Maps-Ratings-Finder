# Maps-Ratings-Finder
With use of a Google API key, it finds the ratings of google maps businesses with a provided link.

===================================
 Google Places Rating Scraper
 READ_ME
===================================
 
OVERVIEW
--------
This tool uses the Google Places API to retrieve business information (ratings,
review counts, address, phone, website) from a list of Google Maps URLs. It
accepts multiple URL formats, processes them in batch, and saves the results
to a CSV file with a JSON summary.
 
 
FILES
-----
  main.py                   - Entry point. Loads API key, runs the scraper.
  places_rating_scraper.py  - Core scraper class (GooglePlacesRatingScraper).
  .env                      - Stores your Google Places API key (you must create this).

REQUIREMENTS
------------
Python 3.7+
 
Install dependencies with:
 
    pip install requests pandas python-dotenv
 
 
SETUP
-----
1. Obtain a Google Places API key from the Google Cloud Console:
   https://console.cloud.google.com/
 
2. Enable the following APIs in your Google Cloud project:
     - Places API
 
3. Create a file named .env in the same directory as main.py with the
   following content:
 
     GOOGLE_PLACES_API_KEY=your_api_key_here
 
4. Prepare your input. In main.py, update the CSV filename and column names
   to match your data file:
 
     df = pd.read_csv('your-file.csv')
     df = df[['google_map_url', 'updated_map_url']]
     OR
     df = df['google_map_url']

USAGE
-----
Run the scraper from the command line:
 
    python main.py
 
On a successful run the scraper will:
  1. Validate your API key against a known place URL.
  2. Load your list of Google Maps URLs.
  3. Process each URL, printing progress to the console.
  4. Save results to company_ratings.csv.
  5. Save a summary to summary.json.
 
 
OUTPUT
------
company_ratings.csv contains one row per business with the following columns:
 
  input           - The original URL passed in
  place_id        - The resolved Google place ID
  name            - Business name
  rating          - Average star rating (1.0 - 5.0)
  total_ratings   - Total number of reviews
  address         - Formatted street address
  phone           - Formatted phone number
  website         - Business website URL
  status          - "success" or "error"
 
summary.json contains aggregate statistics:
 
  total_processed - Total number of URLs attempted
  successful      - Number of successful lookups
  failed          - Number of failed lookups
  total_reviews   - Sum of all review counts across successful results
 
 
ERROR HANDLING
--------------
If a URL cannot be resolved to a place ID, the row will have status "error"
with an explanation in the "error" column. Common causes:
 
  - INVALID_REQUEST : A full URL was passed as a place ID (URL parsing failed)
  - REQUEST_DENIED  : API key is missing, invalid, or lacks Places API access
  - NOT_FOUND       : The place ID was extracted but no matching place exists
  - ZERO_RESULTS    : A search query returned no matching businesses
 
Failed rows are included in the output CSV so you can review and re-process
them manually if needed.

CLASS REFERENCE (places_rating_scraper.py)
------------------------------------------
GooglePlacesRatingScraper(api_key=None)
  Constructor. Reads API key from argument or GOOGLE_PLACES_API_KEY env var.
 
  .test_api_key(url_or_place_id) -> bool
      Validates the API key by making a test Details request.
 
  .extract_place_id(url) -> str | None
      Parses a Google Maps URL and returns the embedded place ID if found.
      Supports ChIJ format and 0x hex format IDs.
 
  .extract_search_query(url) -> str | None
      Extracts and URL-decodes the query string from a /maps/search/ URL.
 
  .find_place_id_by_query(query) -> str | None
      Calls the Places Find Place API to resolve a text query to a place ID.
 
  .get_rating(identifier) -> dict
      Full pipeline for a single URL: extract or resolve place ID, then
      fetch and return business details.
 
  .scrape_batch(businesses, delay=0.1) -> pd.DataFrame
      Processes a list of URLs with a configurable delay between requests.
 
  .save_results(df, ratings_filename, summary_filename)
      Saves the results DataFrame to CSV and writes a JSON summary file.
 
================================================================================
