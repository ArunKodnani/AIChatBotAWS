import os
import json
import boto3


def lambda_handler(event, context):
    
    questionReplies = {"Hi" : "Hi there!", "Hey" : "Hello, How are you today" }
    print (json.dumps(event))
    message = event['messages'][0]['unstructured']['text']
    print (message)
    client = boto3.client('lex-runtime', region_name = 'us-east-1')
    response = client.post_text(
    botName='CustomerServiceBot',
    botAlias='botAlias',
    userId=event['messages'][0]['unstructured']['id'],
    sessionAttributes={
    },
    requestAttributes={
    },
    inputText=message
    )
    messageReply = response['message']
     
    responseBody = {'messages': [{'type': 'string','unstructured': {'id': 'string','text': 'string','timestamp': 'string'}}]}
    responseBody['messages'][0]['unstructured']['text'] = messageReply
    response = {
        'statusCode': 200,
        'headers': { 'Content-Type': 'application/json' },
        'body': responseBody
    }
    
    return response