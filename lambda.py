import os
import json


def lambda_handler(event, context):
    
    questionReplies = {"Hi" : "Hi there!", "Hey" : "Hello, How are you today" }
    print (json.dumps(event))
    message = event['messages'][0]['unstructured']['text']
    print (message)
    if message in questionReplies:
        messageReply = questionReplies[message]
    else:
        messageReply = "Oops, I dont have a response to your request yet"
     
    responseBody = {'messages': [{'type': 'string','unstructured': {'id': 'string','text': 'string','timestamp': 'string'}}]}
    responseBody['messages'][0]['unstructured']['text'] = messageReply
    response = {
        'statusCode': 200,
        'headers': { 'Content-Type': 'application/json' },
        'body': responseBody
    }
    
    return response
    
    
    
    
    