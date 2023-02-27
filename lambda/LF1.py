import json
import datetime
import time
import boto3 

def validate_people_number(slots): 
    people_number = slots['NumberOfPeople']['value']['interpretedValue']
    #print("This is the number of people", people_number)
    return int(people_number) > 0 
    

def validate_date(slots): 

    date_str = slots['DiningTime']['value']['interpretedValue']
    #print("This is today's date:", date_str)
    
    try:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return False 

    if date_obj < datetime.date.today(): 
        return False
    return True

def validate(slots):
    if slots['NumberOfPeople']:
        valid_people = validate_people_number(slots) 
        if not valid_people: 
            return {'isValid':False, 
                    'violatedSlot': 'NumberOfPeople',
                    'message': "I am sorry, you can't have non-positive number of people. Please enter a positive number below" }

    if slots['DiningTime']: 
        valid_date = validate_date(slots)
        if valid_date: 
            return {'isValid':True}
        else: 
           return {'isValid':False, 
                    'violatedSlot': 'DiningTime',
                    'message': "The date you enter can't be in the past. Please enter a date in the future" }
 
                
    return {'isValid': True}

def order(slots):
    location = slots['Location']['value']['interpretedValue']
    cuisine = slots['Cuisine']['value']['interpretedValue']
    dining_date = slots['DiningTime']['value']['interpretedValue']
    people_number = slots['NumberOfPeople']['value']['interpretedValue']
    email = slots['Email']['value']['interpretedValue']
    
    return {
        'location': location, 
        'cuisine': cuisine,
        'dining_date': dining_date, 
        'people_number': people_number,
        'email': email
    }
  
def lambda_handler(event, context):
    
    # print(event)
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    #print(event['invocationSource'])
    #print(slots)
    #print(intent)

    validation_result = validate(slots) 
    if event['invocationSource'] == 'DialogCodeHook':
        if not validation_result['isValid']:
            response = {
            "sessionState": {
                "dialogAction": {
                    'slotToElicit':validation_result['violatedSlot'],
                    "type": "ElicitSlot"
                },
                "intent": {
                    'name':intent,
                    'slots': slots
                    
                    }
            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": validation_result['message']
                }
            ]
            } 
            return response
           
        else:
            response = {
            "sessionState": {
                "dialogAction": {
                    "type": "Delegate"
                },
                "intent": {
                    'name':intent,
                    'slots': slots
                    
                    }
        
            }
        }
            return response
    
    if event['invocationSource'] == 'FulfillmentCodeHook':
        response = {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                'name':intent,
                'slots': slots,
                'state':'Fulfilled'
                
                }
    
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": f"Your request has been recieved successfuly. You will recieve a message on this email address: {slots['Email']['value']['interpretedValue']}"
            }
        ]
        }
        
        # Send this to SQS
        client = boto3.client('sqs')
        resp = client.send_message(
            QueueUrl="https://sqs.us-east-1.amazonaws.com/406150506218/Q1", 
            MessageBody=json.dumps(order(slots)))
        
        
      
        return response
