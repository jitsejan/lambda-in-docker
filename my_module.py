import json
import os

def my_handler(event, context):
    body = {
        "message": "This is the handler",
        "input": event,
        "region": os.environ['AWS_DEFAULT_REGION']
    }
    response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }
    return response
