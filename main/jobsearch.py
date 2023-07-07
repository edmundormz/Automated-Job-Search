import requests
import json
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime, timedelta
import re
import os

#Importing enviroment variables from  file
load_dotenv('./main/.env')

# Set up your API key and other parameters
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')
openai.api_key = os.getenv('OPENAI_API_KEY')

#Create query to search on google for the last 24 hours
today = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
QUERY = f'site:lever.co | site:greenhouse.io "IoT" AND "Manager" AND "Remote" after:{yesterday} before:{today}'
# Construct the API request URL
request_url = f'https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={QUERY}'
# Send the HTTP GET request
google_response = requests.get(request_url)
# Parse the JSON response
data = google_response.json()

# Extract the URLs and titles from the google response and store them in a dict
url_dict = {}
if 'items' in data:
    search_results = data['items']
    for result in search_results:
        url = result['link']
        job_title = result['title']
        url_dict[url] = job_title

#Extracting text from urls using web crawling
def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    return text


#Preprocess the extracted text
def preprocess_text(text):
    # Remove unnecessary whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove non-alphanumeric characters except spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # Convert text to lowercase
    text = text.lower()
    return text

cleaned_text_dict = {}
# Iterate over the URL dict to extract and preprocess text from each URL
for url, job_title in url_dict.items():
    extracted_text = extract_text_from_url(url)
    cleaned_text = preprocess_text(extracted_text)
    cleaned_text_dict[url] = cleaned_text


# Define the function to generate a response from ChatGPT
def generate_chat_response(prompt):
    try:
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=700,
            temperature=0.7,
            n=1,
            stop=None,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        # Extract and return the generated text from the response
        return response.choices[0].text.strip()
    
    except openai.error.InvalidRequestError as e:
        # Handle the exception for InvalidRequestError
        print("Error: Invalid request -", e)
        # Perform any necessary error handling or fallback actions
        # ...
        return 'TLDR'
    
    except Exception as e:
        # Handle any other exceptions
        print("Error:", e)
        # Perform any necessary error handling or fallback actions
        # ...
        return 'TLDR'

# Read my resume
with open('./main/resume.txt','r') as file:
    resume = file.read()

# Read the instructions for the prompt
with open('./main/matching_index_prompt.txt','r') as file:
    index_instructions = file.read()

pre_prompt = f'''{index_instructions}
\nResume:
{resume}'''


matching_positions = {}
for url, job_position in cleaned_text_dict.items():
    prompt = pre_prompt + f''' \nJob description:\n{job_position}'''
    response = generate_chat_response(prompt)
    #Skipping errors
    if response == 'TLDR':
        print('TLDR_ _\n')
        #matching_positions[url] = {'processed': False, 'cleaned_text': job_position, 'match_index': None}
        matching_positions[url] = {'processed': False, 'cleaned_text': None, 'match_index': None}
        continue
    # Search for a two-digit number using regular expression
    match = re.search(r"\b(\d{2})\b", response)
    # Check if a match is found
    if match:
        # Access the matched number using group(0)
        match_index = match.group(0)
    if int(match_index) >= 80:
        matching_positions[url] = {'processed': True, 'cleaned_text': job_position, 'match_index': match_index}

#Add the job title to the matching positions dict
for url,job_title in url_dict.items():
    if url in matching_positions:
        matching_positions[url]['job_title'] = job_title



#for match in matching_positions:
    #ask open ai to generate a cover letter
    #save the cover letter as pdf file
    #send the telegram message
