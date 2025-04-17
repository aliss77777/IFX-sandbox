import os
import csv
import time
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import openai # Added for LLM Summarization

# Load environment variables (for API keys)
load_dotenv() 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o") # Default to gpt-4o if not set

if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in environment variables. Summarization will be skipped.")
    # Or raise an error if summarization is critical:
    # raise ValueError("OPENAI_API_KEY environment variable is required for summarization.")

TARGET_URL = "https://www.ninersnation.com/san-francisco-49ers-news"
OUTPUT_CSV_FILE = "team_news_articles.csv"
DAYS_TO_SCRAPE = 60 # Scrape articles from the past 60 days
REQUEST_DELAY = 1 # Delay in seconds between requests to be polite

# Add a flag to enable/disable summarization easily
ENABLE_SUMMARIZATION = True if OPENAI_API_KEY else False 

def fetch_html(url):
    """Fetches HTML content from a URL with error handling."""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}) # Basic user-agent
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_article_list(html_content):
    """Parses the main news page to find article links and dates."""
    print("Parsing article list page...")
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = []
    # SBNation common structure: find compact entry boxes
    # Note: Class names might change, may need adjustment if scraping fails.
    article_elements = soup.find_all('div', class_='c-entry-box--compact') 
    if not article_elements:
        # Fallback: Try another common pattern if the first fails
        article_elements = soup.find_all('div', class_='p-entry-box') 

    print(f"Found {len(article_elements)} potential article elements.")

    for elem in article_elements:
        # Find the main link within the heading
        heading = elem.find('h2')
        link_tag = heading.find('a', href=True) if heading else None
        
        # Find the time tag for publication date
        time_tag = elem.find('time', datetime=True)
        
        if link_tag and time_tag and link_tag['href']:
            url = link_tag['href']
            # Ensure the URL is absolute
            if not url.startswith('http'):
                 # Attempt to join with base URL (requires knowing the base, careful with relative paths)
                 # For now, we'll rely on SBNation typically using absolute URLs or full paths
                 # from urllib.parse import urljoin
                 # base_url = "https://www.ninersnation.com"
                 # url = urljoin(base_url, url)
                 # Let's assume they are absolute for now based on typical SBNation structure
                 print(f"Warning: Found potentially relative URL: {url}. Skipping for now.")
                 continue # Skip potentially relative URLs

            date_str = time_tag['datetime'] # e.g., "2024-05-20T10:00:00-07:00"
            if url and date_str:
                articles.append((url, date_str))
        else:
             print("Skipping element: Couldn't find link or time tag.") # Debugging

    print(f"Extracted {len(articles)} articles with URL and date.")
    return articles

def parse_article_details(html_content, url):
    """Parses an individual article page to extract details including raw content."""
    print(f"Parsing article details for: {url}")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    details = {
        "title": None,
        "content": None, # This will store the raw content for summarization
        "publication_date": None,
        "link_to_article": url,
        "tags": []
    }

    # Extract Title (Usually the main H1)
    title_tag = soup.find('h1') # Find the first H1
    if title_tag:
        details['title'] = title_tag.get_text(strip=True)
    else:
        print(f"Warning: Title tag (h1) not found for {url}")

    # Extract Publication Date (Look for time tag in byline)
    # SBNation often uses <span class="c-byline__item"><time ...></span>
    byline_time_tag = soup.find('span', class_='c-byline__item')
    time_tag = byline_time_tag.find('time', datetime=True) if byline_time_tag else None
    if time_tag and time_tag.get('datetime'):
        details['publication_date'] = time_tag['datetime']
    else:
        # Fallback: Search for any time tag with datetime attribute if specific class fails
        time_tag = soup.find('time', datetime=True)
        if time_tag and time_tag.get('datetime'):
            details['publication_date'] = time_tag['datetime']
        else:
            print(f"Warning: Publication date tag (time[datetime]) not found for {url}")

    # Extract Content (Paragraphs within the main content div)
    content_div = soup.find('div', class_='c-entry-content')
    if content_div:
        paragraphs = content_div.find_all('p')
        # Join non-empty paragraphs, ensuring None safety
        # Store this raw content for potential summarization
        details['content'] = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]) 
    else:
        print(f"Warning: Content div (div.c-entry-content) not found for {url}")

    # Extract Tags (Look for tags/labels, e.g., under "Filed under:")
    # SBNation often uses a ul/div with class like 'c-entry-group-labels' or 'c-entry-tags'
    tags_container = soup.find('ul', class_='m-tags__list') # A common SBNation tag structure
    if tags_container:
        tag_elements = tags_container.find_all('a') # Tags are usually links
        details['tags'] = list(set([tag.get_text(strip=True) for tag in tag_elements if tag.get_text(strip=True)]))
    else:
        # Fallback: Look for another potential container like the one in the example text
        filed_under_div = soup.find('div', class_='c-entry-group-labels') # Another possible class
        if filed_under_div:
            tag_elements = filed_under_div.find_all('a')
            details['tags'] = list(set([tag.get_text(strip=True) for tag in tag_elements if tag.get_text(strip=True)]))
        else:
            # Specific structure from example text if needed ('Filed under:' section)
            # This requires finding the specific structure around 'Filed under:'
            # Could be more fragile, attempt simpler methods first.
            print(f"Warning: Tags container not found using common classes for {url}")
            # Example: Search based on text 'Filed under:' - less reliable
            # filed_under_header = soup.find(lambda tag: tag.name == 'h2' and 'Filed under:' in tag.get_text())
            # if filed_under_header:
            #     parent_or_sibling = filed_under_header.parent # Adjust based on actual structure
            #     tag_elements = parent_or_sibling.find_all('a') if parent_or_sibling else []
            #     details['tags'] = list(set([tag.get_text(strip=True) for tag in tag_elements]))

    # Basic validation - ensure essential fields were extracted for basic processing
    # Content is needed for summarization but might be missing on some pages (e.g., galleries)
    if not details['title'] or not details['publication_date']:
         print(f"Failed to extract essential details (title or date) for {url}. Returning None.")
         return None 
    
    # Content check specifically before returning - needed for summary
    if not details['content']:
        print(f"Warning: Missing content for {url}. Summary cannot be generated.")

    return details

def is_within_timeframe(date_str, days):
    """Checks if a date string (ISO format) is within the specified number of days from now."""
    if not date_str:
        return False
    try:
        # Parse the ISO format date string, handling potential 'Z' for UTC
        pub_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        
        # Ensure pub_date is offset-aware (has timezone info)
        # If fromisoformat gives naive datetime, assume UTC (common practice for 'Z')
        if pub_date.tzinfo is None or pub_date.tzinfo.utcoffset(pub_date) is None:
             pub_date = pub_date.replace(tzinfo=timezone.utc) # Assume UTC if naive

        # Get current time as an offset-aware datetime in UTC
        now_utc = datetime.now(timezone.utc)
        
        # Calculate the cutoff date
        cutoff_date = now_utc - timedelta(days=days)
        
        # Compare offset-aware datetimes
        return pub_date >= cutoff_date
    except ValueError as e:
        print(f"Could not parse date: {date_str}. Error: {e}")
        return False # Skip if date parsing fails
    except Exception as e:
        print(f"Unexpected error during date comparison for {date_str}: {e}")
        return False

def generate_summary(article_content):
    """Generates a 3-4 sentence summary using OpenAI API."""
    if not ENABLE_SUMMARIZATION or not article_content:
        print("Skipping summary generation (disabled or no content).")
        return "" # Return empty string if summarization skipped or no content
        
    print("Generating summary...")
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Simple prompt for summarization
        prompt = f"""Please provide a concise 3-4 sentence summary of the following article content. 
Focus on the key information and main points. Do not include any information not present in the text. :

---
{article_content}
---

Summary:"""
        
        # Limit content length to avoid excessive token usage (adjust limit as needed)
        max_content_length = 15000 # Approx limit, GPT-4o context window is large but be mindful of cost/speed
        if len(prompt) > max_content_length:
             print(f"Warning: Content too long ({len(article_content)} chars), truncating for summarization.")
             # Truncate content intelligently if needed, here just slicing prompt
             prompt = prompt[:max_content_length] 

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an AI assistant tasked with summarizing news articles concisely."}, 
                {"role": "user", "content": prompt}
            ],
            temperature=0.5, # Adjust for desired creativity vs factuality
            max_tokens=150 # Limit summary length
        )
        
        summary = response.choices[0].message.content.strip()
        print("Summary generated successfully.")
        return summary
        
    except openai.APIError as e:
        print(f"OpenAI API returned an API Error: {e}")
    except openai.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API: {e}")
    except openai.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during summarization: {e}")
        
    return "" # Return empty string on failure

def scrape_and_summarize_niners_nation():
    """Main function to scrape, parse, summarize, and return structured data."""
    print("Starting Niners Nation scraping and summarization process...")
    main_page_html = fetch_html(TARGET_URL)
    if not main_page_html:
        print("Failed to fetch the main news page. Exiting.")
        return []

    articles_on_page = parse_article_list(main_page_html)
    
    scraped_and_summarized_data = []
    now_utc = datetime.now(timezone.utc)
    cutoff_datetime = now_utc - timedelta(days=DAYS_TO_SCRAPE)
    print(f"Filtering articles published since {cutoff_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    processed_urls = set() 

    for url, date_str in articles_on_page:
        if url in processed_urls:
            continue 
            
        if not is_within_timeframe(date_str, DAYS_TO_SCRAPE):
            continue

        print(f"Fetching article: {url}")
        article_html = fetch_html(url)
        if article_html:
            details = parse_article_details(article_html, url)
            if details: 
                # Generate summary if content exists and summarization enabled
                article_summary = "" # Initialize summary
                if details.get('content'):
                    article_summary = generate_summary(details['content'])
                else:
                    print(f"Skipping summary for {url} due to missing content.")
                    
                # Add the summary to the details dictionary
                details['summary'] = article_summary 
                
                # Proceed to structure data (now including the summary)
                structured_row = structure_data_for_csv_row(details) # Use a helper for single row
                if structured_row:
                     scraped_and_summarized_data.append(structured_row)
                     processed_urls.add(url)
                     print(f"Successfully scraped and summarized: {details['title']}")
                else:
                    print(f"Failed to structure data for {url}")

            else:
                 print(f"Failed to parse essential details for article: {url}")
        else:
            print(f"Failed to fetch article page: {url}")
            
        print(f"Waiting for {REQUEST_DELAY} second(s)...")
        time.sleep(REQUEST_DELAY)
        
    print(f"Scraping & Summarization finished. Collected {len(scraped_and_summarized_data)} articles.")
    return scraped_and_summarized_data

def structure_data_for_csv_row(article_details):
    """Processes a single article's details into the final CSV structure."""
    current_year = datetime.now().year
    
    # Extract and parse publication date to get the year
    season = current_year # Default to current year
    pub_date_str = article_details.get("publication_date")
    if pub_date_str:
        try:
            pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
            season = pub_date.year
        except ValueError:
            print(f"Warning: Could not parse date '{pub_date_str}' for season. Using default {current_year}.")
    
    # Get tags and format as topic string
    tags = article_details.get("tags", [])
    topic = ", ".join(tags) if tags else "General News" 

    # Build the dictionary for the CSV row
    structured_row = {
        "Team_name": "San Francisco 49ers", 
        "season": season,
        "city": "San Francisco", 
        "conference": "NFC", 
        "division": "West", 
        "logo_url": "", 
        "summary": article_details.get("summary", ""), # Get the generated summary
        "topic": topic,
        "link_to_article": article_details.get("link_to_article", ""),
    }
    return structured_row
    
def write_to_csv(data, filename):
    """Writes the structured data to a CSV file."""
    if not data:
        print("No data to write to CSV.")
        return
        
    fieldnames = [
        "Team_name", "season", "city", "conference", "division", 
        "logo_url", "summary", "topic", "link_to_article"
    ]
    
    if not all(key in data[0] for key in fieldnames):
        print(f"Error: Mismatch between defined fieldnames and data keys.")
        print(f"Expected: {fieldnames}")
        print(f"Got keys: {list(data[0].keys())}")
        return
        
    print(f"Writing {len(data)} rows to {filename}...")
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Successfully wrote {len(data)} rows to {filename}")
    except IOError as e:
        print(f"Error writing to CSV file {filename}: {e}")
    except Exception as e:
         print(f"An unexpected error occurred during CSV writing: {e}")

# --- Main Execution --- 
if __name__ == "__main__":
    # Call the main orchestrator function that includes summarization
    processed_articles = scrape_and_summarize_niners_nation()
    
    if processed_articles:
        write_to_csv(processed_articles, OUTPUT_CSV_FILE)
    else:
        print("No articles were processed.") 