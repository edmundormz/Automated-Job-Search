import os
import re
import requests
import boto3
import openai
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv
from urllib.parse import quote

# Load environment variables
load_dotenv()

# Set up environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
S3_MATCHING_INDEX_PROMPT_KEY = os.getenv('S3_MATCHING_INDEX_PROMPT_KEY')
S3_RESUME_OBJECT_KEY = os.getenv('S3_RESUME_OBJECT_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY

s3_client = boto3.client('s3')

# Helper functions
def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser') #???
    return soup.get_text()

def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text.lower()

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
        return response.choices[0].text.strip()

    except openai.error.InvalidRequestError as e:
        print("Error: Invalid request -", e)
        return 'TLDR'

    except Exception as e:
        print("Error:", e)
        return 'TLDR'

def send_telegram(message):
    message = quote(message)  # URL encode the message
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        #print(response.json())
    except requests.exceptions.HTTPError as err:
        print(f"Error sending message: {err}")

# Main Lambda handler. This should be the main function in order to run in AWS Lambda
def lambda_handler(event, context):
    #Get today's and yesterday dates for the google query
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    #This is the actual query for Google search. It may be modified as requested
    QUERY = f'site:lever.co | site:greenhouse.io "IoT" AND "Manager" AND "Remote" after:{yesterday} before:{today}'
    request_url = f'https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={QUERY}'
    google_response = requests.get(request_url)
    data = google_response.json()

    url_dict = {}
    if 'items' in data:
        for result in data['items']:
            url_dict[result['link']] = result['title']

    cleaned_text_dict = {url: preprocess_text(extract_text_from_url(url)) for url in url_dict.keys()}

    #Get the resume from an S3 location
    resume = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_RESUME_OBJECT_KEY)['Body'].read().decode('utf-8')
    #Get the prompt instructions from an S3 location
    index_instructions = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_MATCHING_INDEX_PROMPT_KEY)['Body'].read().decode('utf-8')
    #Builds the prompt to send to open ai
    pre_prompt = f'''{index_instructions}\nResume:\n{resume}'''

    matching_positions = {}
    for url, job_position in cleaned_text_dict.items():
        prompt = pre_prompt + f'''\nJob description:\n{job_position}'''
        response = generate_chat_response(prompt)
        if response == 'TLDR':
            matching_positions[url] = {'processed': False, 'cleaned_text': None, 'match_index': None}
            continue
        match = re.search(r"\b(\d{2})\b", response)
        if match:
            match_index = int(match.group(0))
            if match_index >= 80:
                matching_positions[url] = {'processed': True, 'cleaned_text': job_position, 'match_index': match_index}

    #Assign the job title to matching positions
    for url in matching_positions.keys():
        matching_positions[url]['job_title'] = url_dict.get(url, '')

    for url, data in matching_positions.items():
        message = f'New job match!\n{data["job_title"]}\nMatch index: {data["match_index"]}\n{url}'
        send_telegram(message)
