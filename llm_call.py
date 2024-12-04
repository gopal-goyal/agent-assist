import os
from dotenv import load_dotenv
from groq import Groq
import json
import re
from datetime import datetime, timedelta

load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')

client = Groq(
    api_key=groq_api_key
)

def get_default_dates():
    # Calculate the default start and end dates
    current_date = datetime.utcnow().strftime('%Y-%m-%d')
    one_year_ago = (datetime.utcnow() - timedelta(days=365)).strftime('%Y-%m-%d')
    return current_date, one_year_ago

def llm_call(prompt):
    # Get the default dates
    current_date, one_year_ago = get_default_dates()

    system_prompt = f"""
    You are tasked with extracting the following details from the query:

    {prompt}

    Your task is to extract the following information:
    1. Entity: The company name mentioned in the query (e.g., Flipkart, Amazon).
    2. Parameter: The performance metric mentioned (e.g., GMV, revenue, profit).
    3. Start Date: The start date for the time period in the query (in ISO 8601 format). If no date is specified, use the default: {one_year_ago}.
    4. End Date: The end date for the time period in the query (in ISO 8601 format). If no date is specified, use the default: {current_date}.
    
    Please return the extracted information strictly in the following JSON format without any additional text or explanations:

    ```json
    [
        {{
            "entity": "<company_name>",
            "parameter": "<metric_name>",
            "startDate": "<start_date_iso>",
            "endDate": "<end_date_iso>"
        }}
    ]
    """
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": system_prompt,
            }
        ],
        model="llama3-8b-8192",
    )
    
    # Extract the content of the LLM's response
    content = chat_completion.choices[0].message.content

    # Use regular expression to find the JSON-like structure
    json_match = re.search(r'\[.*\]', content, re.DOTALL)

    if json_match:
        # Extract the matched JSON portion and parse it
        json_string = json_match.group(0)
        try:
            response_data = json.loads(json_string)
            return response_data
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON", "content": content}
    else:
        return {"error": "No valid JSON found in the response", "content": content}
