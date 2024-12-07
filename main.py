import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def scrape_visa_wait_times():
    # URL of the page
    url = "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/global-visa-wait-times.html"
    
    try:
        # Send GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table
        table = soup.find('table')
        
        if not table:
            raise Exception("Table not found on the page")
        
        # Initialize lists to store data
        data = []
        headers = []
        
        # Extract headers
        for th in table.find_all('th'):
            # Clean up header text
            header = re.sub(r'\s+', ' ', th.text.strip())
            headers.append(header)
        
        # Extract rows
        for row in table.find_all('tr')[1:]:  # Skip header row
            cols = row.find_all('td')
            if cols:
                row_data = []
                for col in cols:
                    # Clean up cell text
                    cell_text = col.text.strip()
                    if cell_text == '':
                        cell_text = 'N/A'
                    row_data.append(cell_text)
                data.append(row_data)
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)
        
        # Save to CSV
        csv_filename = 'visa_wait_times.csv'
        df.to_csv(csv_filename, index=False)
        print(f"Data successfully scraped and saved to {csv_filename}")
        
        return df
        
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
    except Exception as e:
        print(f"Error processing the data: {e}")
        return None

if __name__ == "__main__":
    scrape_visa_wait_times()