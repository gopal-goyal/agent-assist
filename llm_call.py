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
    You are tasked with extracting specific details from the query, accounting for variations in user input and maintaining accuracy.
    Utilize semantic understanding to identify and normalize the following details accurately:

    {prompt}

    Your task is to extract the following information:
    1. Entity: The company name mentioned in the query (e.g., Flipkart, Amazon). Consider variations, abbreviations, or alternative spellings (e.g., "Flip Kart" or "AMZN" for Flipkart and Amazon, respectively).
    2. Parameter: The performance metric mentioned (e.g., GMV, revenue, profit). Account for synonyms, acronyms, or alternative terms (e.g., "Gross Merchandise Value" for GMV).
    3. Start Date: The start date for the time period in the query (in ISO 8601 format). If relative date ranges are provided (e.g., "last quarter", "previous month"), calculate the appropriate ISO 8601 date. If no date is specified, use the default: {one_year_ago}.
    4. End Date: The end date for the time period in the query (in ISO 8601 format). If no date is specified, use the default: {current_date}.

    If the query asks for comparisons across multiple companies (for example, comparing Amazon and Flipkart), you must provide the extracted details for each company separately as distinct objects in the same JSON response. 
    Each object should represent one company and its corresponding performance metrics, with "entity" representing the company, "parameter" the performance metric, and the relevant dates for that company.

    For example, if a query asks for data for Amazon and Flipkart, you should return a JSON like this:

    ```json
    [
        {{
            "entity": "Amazon",
            "parameter": "revenue",
            "startDate": "2023-01-01",
            "endDate": "2023-12-31"
        }},
        {{
            "entity": "Flipkart",
            "parameter": "GMV",
            "startDate": "2023-01-01",
            "endDate": "2023-12-31"
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
