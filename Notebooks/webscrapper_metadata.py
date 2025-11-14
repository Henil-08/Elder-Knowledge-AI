from typing import List
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

def scrape_links_and_text(main_page_url):
    """
    Finds links on a main page, visits each one, and scrapes text.
    """
    # --- Part 1: Get the Main Page ---
    try:
        # Set a User-Agent to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(main_page_url, headers=headers)
        response.raise_for_status() # Raise an error for bad responses (4xx or 5xx)
    except requests.RequestException as e:
        print(f"Error fetching main page {main_page_url}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # --- Part 2: Find All "Certain Links" ---
    #
    # !!! YOU MUST CUSTOMIZE THIS SELECTOR !!!
    # Use your browser's "Inspect" tool to find the right tag and class.
    # Example: 'a.article-link' (all <a> tags with class="article-link")
    # Example: 'div.post-preview > h2 > a' (all <a> tags inside <h2> inside <div class="post-preview">)
    #
    link_elements = soup.select('.text-image-right ul li a') # class text-image-right contains the links
    if not link_elements:
        print("No links found with that selector. Check your CSS selector.")
        return

    print(f"Found {len(link_elements)} links to scrape.")
    
    scraped_data = {}

    # --- Part 3: Loop Through Links and Scrape Text ---
    for link in link_elements:
        # Get the URL from the 'href' attribute
        link_url = link.get('href')
        
        # Handle relative URLs (e.g., /page/about)
        full_url = urljoin(main_page_url, link_url)
        
        print(f"Scraping {full_url}...")
        
        try:
            article_response = requests.get(full_url, headers=headers)
            article_response.raise_for_status()
            
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            
            # --- Part 4: Extract Text from the Link's Page ---
            #
            # !!! YOU MUST CUSTOMIZE THIS SELECTOR !!!
            # Find the main content block (e.g., <article>, <div id="content">)
            #
            content_block = article_soup.select_one('p') #get all text within <p> tags
            
            if content_block:
                # Get text, strip whitespace, and use a space as a separator
                text = content_block.get_text(separator=' ', strip=True)
                scraped_data[full_url] = text
            else:
                print(f"  > Could not find content block on {full_url}")

        except requests.RequestException as e:
            print(f"  > Error fetching {full_url}: {e}")
            
    return scraped_data

if __name__ == "__main__":
    # 1. Set the URL of the page that *contains* all the links
    STARTING_URLS: List[str] = [
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/multiculturalvoices/african-americans/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/multiculturalvoices/asian-americans/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/multiculturalvoices/latinx/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/multiculturalvoices/jewish/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/multiculturalvoices/lgbtq/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/multiculturalvoices/native-americans/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/forestryvoices/forestservice/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/forestryvoices/scientists/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/climatevoices/bachelet/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/climatevoices/bethel/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/climatevoices/boudet/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/climatevoices/clark/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/climatevoices/hanauska/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/climatevoices/jaeger/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/climatevoices/law/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/climatevoices/mote/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/climatevoices/ruggiero/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/climatevoices/schmittner/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/climatevoices/thompson/",
        "https://scarc.library.oregonstate.edu/omeka/exhibits/show/climatevoices/trelstad/"
    ]
    
   # List to hold DataFrames from all scraped pages
    all_data_frames: List[pd.DataFrame] = []
    
    print(f"Starting scrape across {len(STARTING_URLS)} collections...")
    print("-" * 30)

    # 2. Loop through the list of URLs
    for url in STARTING_URLS:
        # Extract the collection name for tagging the data
        collection_name = url.split("/")[-2] 
        print(f"\nProcessing Collection: **{collection_name.upper()}**")
        
        all_text_data = scrape_links_and_text(url)
        
        if all_text_data:
            # Create a DataFrame for the current collection's data
            metadata_df = pd.DataFrame(list(all_text_data.items()), columns=['URL', 'Text'])
            
            # Data cleaning/tagging
            metadata_df['ID'] = metadata_df['URL'].str.extract(r'(\d+)$')  # extract last number from URL
            metadata_df['Collection'] = collection_name
            
            all_data_frames.append(metadata_df)
    
    # 3. Consolidate and Save the Results
    if all_data_frames:
        final_df = pd.concat(all_data_frames, ignore_index=True)
        OUTPUT_FILENAME = 'oral_history_scraped_metadata.csv'
        final_df.to_csv(OUTPUT_FILENAME, index=False)
        
        print("\n" + "=" * 30)
        print(f"SCRAPING SUCCESSFUL!")
        print(f"Total entries scraped: {len(final_df)}")
        print(f"Consolidated metadata saved to: **{OUTPUT_FILENAME}**")
        print("=" * 30)
    else:
        print("\nSCRAPING FAILED: No data was successfully scraped from any URL.")