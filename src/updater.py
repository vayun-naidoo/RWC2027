import requests
from bs4 import BeautifulSoup
import json

# Prevent website blocking by setting a user-agent for browser
headers ={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# Get response from the Wikipedia page
url = 'https://en.wikipedia.org/wiki/World_Rugby_Rankings'
response = requests.get(url, headers=headers)

# Check if responses are valid
if response.status_code == 200:
    print("Success! We have the website data.")
else:
    print(f"Failed to access site: {response.status_code}")

# Create a BeautifulSoup object to parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')
# Get the instance of the rankings table
table = soup.find('table', class_='wikitable floatright sticky-header')

scraped_data = {}

rows = table.find_all('tr')[1:]  # Skip the header row

for row in rows:   
    cols = row.find_all('td')
    if len(cols) > 2:
        # Get team information
        team_name = cols[1].get_text(strip=True)
        points = cols[2].get_text(strip=True)[1:]         
        # Save it to our dictionary
        scraped_data[team_name] = float(points)

# Save the scraped data to a JSON file
with open('data/teams.json', 'w') as f:
    json.dump(scraped_data, f, indent=4)