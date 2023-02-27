import json
import os
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import random 

REGION = 'us-east-1'
HOST = 'search-restaurant-yuzwiqbtqvppg3tfdnbaibnjia.us-east-1.es.amazonaws.com'
INDEX = 'restaurants'

def lambda_handler(event, context):
    # Set up the SQS client
    sqs = boto3.client('sqs')

    # Get the URL of the SQS queue
    queue_url = 'https://sqs.us-east-1.amazonaws.com/406150506218/Q1'

    # Poll the SQS queue for messages
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20,
    )

    # what we get form sqs
    for message in response.get('Messages', []):
        message_body = message['Body']
        message_body = json.loads(message_body)
        
        
        # results from open search
        results = query(message_body['cuisine'])
        restaurant_list = []
        for result in results: 
            
            # id of the restaurants ( for dynamo lookup)
            id = result['id']
            restaurant_list += [get_data_dynamo(id)]
            #(dynamo-restaurant list ,   sqs message)
            #print(restaurant_list)
        
        email_body = format_body(random.sample(restaurant_list, 5), message_body)
        #print(message_body[])
        send_email_test(message_body, email_body)
        receipt_handle = message['ReceiptHandle']
        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle )
            
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
        },
        'body': json.dumps({'results': results})
    }
def query(term):
    q = { 'query': {'multi_match': {'query': term}}}
    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)
    res = client.search(index=INDEX, body=q)
    hits = res['hits']['hits']
    results = []
    for hit in hits:
        results.append(hit['_source'])
    return results
def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)



#---------------------------------------------
def format_body(db_query_results, sqs_query_results ): 
    
    Message = f"Hello there! \n\nHere are my 5  {sqs_query_results['cuisine'].capitalize()} restaurant suggestions for {sqs_query_results['people_number']} people on {sqs_query_results['dining_date']} :"
    Message += "\n"
    counter = 1
    for db_query_result in db_query_results:
        print(db_query_result)
        address = db_query_result['address']['S']
        url = db_query_result['url']['S']
        name = db_query_result['name']['S']
        cuisine = db_query_result['cuisine']['S']
        
        Message += str(counter) + ") " 
        Message += name + " found at " + address + ". You can find more information here: " + url + ".\n"
        counter += 1 
    
    Message += " \n Enjoy your meal! "
    
    return Message
    
    
def send_email_test(sqs_message, email_body):
    
    ses = boto3.client('ses', region_name='us-east-1')

    # Define the email message
    sender = 'bam2243@columbia.edu'
    recipient = sqs_message['email']
    subject = 'Dining Concierge Restaurant Recommendations!'
    

    # Send the email
    response = ses.send_email(
        Source=sender,
        Destination={
            'ToAddresses': [
                recipient
            ]
        },
        Message={
            'Subject': {
                'Data': subject
            },
            'Body': {
                'Text': {
                    'Data': email_body
                }
            }
        }
    )

    # Log the response from SES


#---------------------------------------------


def get_data_dynamo(id):
    # Create a DynamoDB client
    dynamodb = boto3.client('dynamodb')
    
    # Define the table name and item ID
    table_name = 'Dynamo_manual'

    # Retrieve the item from the table
    response = dynamodb.get_item(
        TableName=table_name,
        Key={
            'ID': {'N': id}
        }
    )
    # Extract the item data from the response
    item = response.get('Item', {})
    return item
    # Print the item data

