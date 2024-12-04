from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from llm_call import llm_call

load_dotenv()

app = Flask(__name__)

# Replace this with your actual API key
API_KEY = os.getenv("API_KEY")

# Error response for unauthorized access
def unauthorized_response():
    return jsonify({"error": "Unauthorized access. Invalid or missing API key."}), 401

# Middleware to check API key
@app.before_request
def verify_api_key():
    api_key = request.headers.get("x-api-key")
    if not api_key or api_key != API_KEY:
        return unauthorized_response()

# GET method
@app.route('/api/resource', methods=['GET'])
def get_resource():
    return jsonify({"message": "This is a GET response", "data": "Your resource data"})

# POST method
@app.route('/api/resource', methods=['POST'])
def post_resource():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    #Processing Here
    query = data.get('query')
    response = llm_call(query)
    return jsonify({"message": "POST request received", "received_data": data, "response": response})

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)


