import requests
import json

# Set up your API key and other parameters
API_KEY = 'AIzaSyB68PuzI6m_GMHBSfZZycpC-pNkodIzEz4'
SEARCH_ENGINE_ID = 'b75e4a3cf9d204a8c'
QUERY = 'site:lever.co | site:greenhouse.io "IoT" AND "Manager" AND "Remote" after:2023-07-03 before:2023-07-04'

# Construct the API request URL
url = f'https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={QUERY}'

# Send the HTTP GET request
response = requests.get(url)

# Parse the JSON response
data = response.json()

# Save the JSON response to a file
with open('search_results.json', 'w') as file:
    json.dump(data, file)

# Extract relevant information from the response
if 'items' in data:
    search_results = data['items']
    for result in search_results:
        url = result['link']
        title = result['title']
        snippet = result['snippet']
        print(f"URL: {url}\nTitle: {title}\nSnippet: {snippet}\n\n")
else:
    print("No search results found.")
