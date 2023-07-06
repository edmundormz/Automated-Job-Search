import requests
import json
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime, timedelta
import re
import os
#Importing enviroment variables from  file
load_dotenv('.env')

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
# # Save the JSON response to a file
# with open('search_results.json', 'w') as file:
#     json.dump(data, file)

# Extract the URLs from the google response and store them in a list
url_list = []
if 'items' in data:
    search_results = data['items']
    for result in search_results:
        url = result['link']
        url_list.append(url)

#Extracting text from urls using web crawling
def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    return text

# #Saving the extracted text and its url in a dict
# extracted_text_dict = {}
# for url in url_list:
#     extracted_text = extract_text_from_url(url)
#     extracted_text_dict[url] = extracted_text

# #Save the extracted text in a file in the proper encoding
# output_file = "extracted_text_list.txt"
# with open(output_file, 'w', encoding='utf-8') as file:
#     file.write('\n'.join(extracted_text_list))

#Preprocess the extracted text
def preprocess_text(text):
    # Remove unnecessary whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove non-alphanumeric characters except spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # Convert text to lowercase
    text = text.lower()
    return text

#cleaned_text_list = [preprocess_text(text) for text in extracted_text_list]
cleaned_text_dict = {}

# Iterate over the URL list and extract text from each URL
for url in url_list:
    extracted_text = extract_text_from_url(url)
    cleaned_text = preprocess_text(extracted_text)
    cleaned_text_dict[url] = cleaned_text

json_file_path = 'cleaned_text_dict.json'
with open(json_file_path,'w') as json_file:
    json.dump(cleaned_text_dict, json_file)

# Define the function to generate a response from ChatGPT
def generate_chat_response(prompt):
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
    #handle exceptions instead of better preprocessing text

    # Extract and return the generated text from the response
    return response.choices[0].text.strip()

# Read my resume
with open('resume.txt','r') as file:
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
    # Search for a two-digit number using regular expression
    match = re.search(r"\b(\d{2})\b", response)
    # Check if a match is found
    if match:
        # Access the matched number using group(0)
        match_index = match.group(0)
    if int(match_index) >= 80:
        matching_positions[url] = {'url': url, 'cleaned_text': job_position, 'match_index': match_index}
    
json_file_path = 'matching_positions.json'
with open(json_file_path,'w') as json_file:
    json.dump(matching_positions, json_file)

#for match in matching_positions:
    #ask open ai to generate a cover letter
    #save the cover letter as pdf file
    #send the telegram message





#

# #Save the extracted text in a file in the proper encoding
# output_file = "cleaned_text_list.txt"
# with open(output_file, 'w', encoding='utf-8') as file:
#     file.write('\n##NEW JOB##""\n'.join(cleaned_text_list))


# # Extract relevant information from the response
# if 'items' in data:
#     search_results = data['items']
#     for result in search_results:
#         url = result['link']
#         title = result['title']
#         snippet = result['snippet']
#         print(f"URL: {url}\nTitle: {title}\nSnippet: {snippet}\n\n")
# else:
#     print("No search results found.")

# #Invoke OpenAI API
# response = openai.Completion.create(
#     engine='text-davinci-003',
#     prompt='Prompt text goes here',
#     max_tokens=100,
#     temperature=0.7
# )
#
#generated_text = response.choices[0].text.strip()

