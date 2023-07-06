import openai

# Set up your OpenAI API credentials
openai.api_key = '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'

# Read my resume
with open('resume.txt','r') as file:
    resume = file.read()
# Read the instructions for the prompt
with open('matching_index_prompt.txt','r') as file:
    index_instructions = file.read()
# This should be iterating from a list
job_description = 'job application for technical account manager at hivemq technical account manager at hivemq view all jobs united states remote grow with hivemq as we lead iot messaging and connectivity we are a fastgrowing tech startup looking to add to our team of innovative and motivated people hivemq is a messaging platform for reliable secure and scalable data movement to and from connected iot devices our vision is a connected world where people and companies can unleash their full potential our flagship product the hivemq mqtt broker is used by over 130 customers to develop new connected products improve efficiencies and drive down costs hivemq originated in landshut germany and has grown into a global remotefirst company the last time we counted we spoke 32 languages within hivemq join us as we work to contribute to the fast moving development of the iot ecosystem and help companies enable mission critical use cases like connected cars logistics industry 40 and connected iot products hivemqs vision for this role as a technical account manager you will be an integral part of our customer success team tams serve as the technical point of contact for our key customers and act as advocates for our customers towards internal teams you will be making sure our clients receive top service by maintaining relationships with hivemqs current technical champions addressing their technical needs and keeping a regular bidirectional communication channel open with them through your exceptional relationship building skills you will help identify new champions and help identify new opportunities to expand hivemqs adoption within our existing customer base you will increase our customers trust in and success with the hivemq platform proactively help customers with current and future challenges by demonstrating how various products and services can be best utilized utilize your customer facing skills as you will checkin with our customers regularly and provide architectural support support them in building technical proofs of concept and showcase new products internally represent the customers voice towards the hivemq product management to ensure our products continue to provide the best possible value for our customers work in close collaboration with the hivemq technical support team to guarantee that our documentation and knowledge base constantly improves keeping our ease of use promise understand our customers longterm success criteria and communicate those internally so that we can continue working in long lasting partnership like relationships and help our clients succeed you have at least a bachelors degree in a related technical field or equivalent practical experience customerfacing experience interfacing with executive stakeholders driving technical implementation or transformation programs experience in distributed systems with messaging or database technology experience in designing architecture and proofs of concept the ability to manage competing priorities excellent written and verbal communication skills in english german is a plus worked in a customer success role with a software company providing onpremise services before excerpt from our customer list httpswwwhivemqcomcustomers informations about our job advertisements job advertisements of hivemq gmbh are always directed at female male and various applicants regardless of age gender religion sexual identity disability race ethnic origin world view etc the selection of a candidate is exclusively based on qualifications for organisational reasons we cannot return application documents and cannot reimburse any expenses that you incur during the application process apply for this job  required first name  last name  email  phone  resumecv  drop files here attach dropbox or enter manually file types pdf doc docx txt rtf cover letter drop files here attach dropbox or enter manually file types pdf doc docx txt rtf linkedin profile website do you live in eastern time zone   yes no what does rbac stands for in modern technogy  what is the difference between using a virtual machine vs a container  privacy request i have read and understood hivemqs privacy policy please selectconfirm please reach out to our support team via our help center '

prompt = f'''{index_instructions}
\nResume:
{resume}
\nJob description:
{job_description}'''

with open('index_prompt.txt','w') as file:
     file.write(prompt)


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

    # Extract and return the generated text from the response
    return response.choices[0].text.strip()

# Example usage
#prompt = "What is the weather like today in Austin, TX?"
response = generate_chat_response(prompt)
print(response)
