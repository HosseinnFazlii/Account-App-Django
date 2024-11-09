from sms_ir import SmsIr
from decouple import config

def send_verification_code(mobile, code):
    api_key = config('SMSIR_API_KEY')
    line_number = config('SMSIR_LINE_NUMBER')
    sms_ir = SmsIr(api_key, line_number)

    # Assuming you have a predefined template with a placeholder for the code
    template_id = 123456  # Replace with your actual template ID
    parameters = [
        {"name": "Code", "value": code}
    ]

    try:
        response = sms_ir.send_verify_code(mobile, template_id, parameters)
        if response['status'] == 1:
            return True, response['data']
        else:
            return False, response['message']
    except Exception as e:
        return False, str(e)
