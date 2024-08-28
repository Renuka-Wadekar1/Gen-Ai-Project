from flask import Flask, request, jsonify, render_template
import requests
import logging
import certifi  # Library to provide Mozilla's CA Bundle

app = Flask(__name__)

# Azure OpenAI details
AZURE_OPENAI_ENDPOINT = "https://openai.azure.com/"  # Replace with your Azure OpenAI endpoint
AZURE_OPENAI_API_KEY = "API Key"  # Replace with your Azure OpenAI API key

# Set up logging
logging.basicConfig(level=logging.INFO)  # Change to DEBUG for more detailed logs

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/messages', methods=['POST'])
def api_messages():
    try:
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        headers = {
            "Content-Type": "application/json",
            "api-key": AZURE_OPENAI_API_KEY  # Changed from Authorization to api-key
        }
        data = {
            "messages": [{"role": "user", "content": user_message}]
        }

        # Perform the POST request with SSL verification
        response = requests.post(
            f"https://hv-openai-lab68.openai.azure.com/openai/deployments/Plastic_Boat/chat/completions?api-version=2024-02-15-preview",
            json=data,
            headers=headers,
            verify=certifi.where()  # Use certifi's CA Bundle for SSL verification
        )

        if response.status_code == 200:
            response_data = response.json()
            bot_response = response_data['choices'][0]['message']['content']
            return jsonify({"response": bot_response})
        else:
            error_message = f"Error from Azure OpenAI: {response.status_code} {response.text}"
            logging.error(error_message)  # Log the error message
            return jsonify({"error": "Failed to get a response from Azure OpenAI"}), response.status_code
    except requests.exceptions.SSLError as ssl_err:
        # Handle SSL-specific errors
        error_message = f"SSL Error: {str(ssl_err)}"
        logging.error(error_message)  # Log the SSL error
        return jsonify({"error": "SSL Certificate Verification Failed"}), 500
    except requests.exceptions.RequestException as req_err:
        # Handle other request-related errors
        error_message = f"Request Error: {str(req_err)}"
        logging.error(error_message)  # Log the request error
        return jsonify({"error": "Request Failed"}), 500
    except Exception as e:
        # Handle other unexpected errors
        error_message = f"Exception: {str(e)}"
        logging.error(error_message)  # Log the exception
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
