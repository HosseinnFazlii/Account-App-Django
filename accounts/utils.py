import requests
from decouple import config

def send_verification_code(phone_number, otp):
    # Load your API key
    api_key = config('SMSIR_API_KEY')
    # Define the SMS API endpoint
    url = "https://api.sms.ir/v1/send/verify"
    # Set the headers with your API key
    headers = {"x-api-key": api_key}
    # Create the payload to be sent in the request
    payload = {
        "mobile": phone_number,
        "templateId": 728141,  # Replace with your actual template ID from SMS.ir
        "parameters": [
            {
                "name": "Code",
                "value": otp
            }
        ]
    }

    # Send the POST request to the SMS API
    response = requests.post(url, json=payload, headers=headers)
    
    # Check if the response was successful
    if response.status_code == 200:
        return True, "OTP sent successfully"
    else:
        # Attempt to retrieve an error message if available
        try:
            error_message = response.json().get("message", "Unknown error")
        except ValueError:
            error_message = "Failed to parse error response"
        return False, f"Failed to send OTP: {error_message}"
