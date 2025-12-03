import requests
from bs4 import BeautifulSoup
import json

# Prevent website blocking by setting a user-agent for browser
headers ={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

confirmed_teams = {
    # Pool A
    'New Zealand': 'A',
    'Australia' : 'A',
    'Chile': 'A',
    'Hong Kong': 'A',

    # Pool B
    'South Africa': 'B',
    'Italy': 'B',
    'Georgia': 'B',
    'Romania': 'B',
    
    # Pool C
    'Argentina': 'C',
    'Fiji': 'C',
    'Spain': 'C',
    'Canada': 'C',

    # Pool D
    'Ireland': 'D',
    'Scotland': 'D',
    'Uruguay': 'D',
    'Portugal': 'D',

    # Pool E
    'France': 'E',
    'Japan': 'E',
    'United States': 'E',
    'Samoa': 'E',

    # Pool F
    'England': 'F',
    'Wales': 'F',
    'Tonga': 'F',
    'Zimbabwe': 'F',
    
}


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

scraped_data = {'teams' : []}

rows = table.find_all('tr')[1:]  # Skip the header row

for row in rows:   
    cols = row.find_all('td')
    if len(cols) > 2:
        # Get team information
        team_name = cols[1].get_text(strip=True)
        wr_points = cols[2].get_text(strip=True)[1:]

        if team_name in confirmed_teams:
            # Save it to our dictionary
            scraped_data['teams'].append({'team_name':  team_name, 
                                          'wr_points':  float(wr_points), 
                                          'pool':       confirmed_teams[team_name]})
        
# Save the scraped data to a JSON file
with open('data/teams.json', 'w') as f:
   json.dump(scraped_data, f, indent=4)