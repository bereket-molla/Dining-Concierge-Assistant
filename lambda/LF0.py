import time
import boto3
import json
# Define the client to interact with Lex
client = boto3.client('lexv2-runtime')
def lambda_handler(event, context):
    msg_from_user = event['messages'][0]['unstructured']['text'] 
    # change this to the message that user submits on 
    # your website using the 'event' variable
    #msg_from_user = "Bye"
    print(event)
    print(f"Message from frontend: {msg_from_user}")
    # Initiate conversation with Lex
    response = client.recognize_text(
            botId='TP033AYLSW',
            botAliasId='QXQAZTY1R4',
            localeId='en_US',
            sessionId='testuser',
            text=msg_from_user)
    
    msg_from_lex = response.get('messages', [])
    if msg_from_lex:
        
        print(f"Message from Chatbot: {msg_from_lex[0]['content']}")
        print(response)
        
        resp = {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': 'http://cloud-concierge.s3-website-us-east-1.amazonaws.com',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'messages':[{
                        'type': 'unstructured',
                        'unstructured': {
                            'id': '1', 
                            'text': msg_from_lex[0]['content'], 
                            'timestamp': str(time.time())                     }
            }]
        }
        
        # modify resp to send back the next question Lex would ask from the user
        
        # format resp in a way that is understood by the frontend
        # HINT: refer to function insertMessage() in chat.js that you uploaded
        # to the S3 bucket
        return resp

# ------------------------------------------------



