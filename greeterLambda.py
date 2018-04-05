import calendar
import datetime
import dateutil.parser
import re
import boto3
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def validate_cuisine(cuisine_type):
    cuisine_types = ['chinese','thai','asian','indian','american','japanese']
    if(cuisine_type):
        return cuisine_type.lower() in cuisine_types
    
def validate_city(city):
    US_cities = ['new york', 'los angeles', 'chicago', 'houston', 'philadelphia', 'phoenix', 'san antonio',
                    'san diego', 'dallas', 'san jose', 'austin', 'jacksonville', 'san francisco', 'indianapolis',
                    'columbus', 'fort worth', 'charlotte', 'detroit', 'el paso', 'seattle', 'denver', 'washington dc',
                    'memphis', 'boston', 'nashville', 'baltimore', 'portland','brooklyn']
                    
    if(city):
        return city.lower() in US_cities
    
def validate_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except:
        return False
        
def validate_contact(contact):
    contact = str.replace(contact,'-','')
    contact = str.replace(contact,'(','')
    contact = str.replace(contact,')','')
    contact = str.replace(contact,' ','')
    if(len(contact) == 12 or len(contact) == 11):
        if((contact[0] == '+' and contact[1] == '1') or contact[0] == '1'):
            return True
        else:
            return False
    else:
        return False
        
def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def validate_userDetails(cuisine_type,city,date,contact):
    cuisine_types = ['chinese','thai','asian','indian','american','japanese']
    
    US_cities = ['new york', 'los angeles', 'chicago', 'houston', 'philadelphia', 'phoenix', 'san antonio',
                    'san diego', 'dallas', 'san jose', 'austin', 'jacksonville', 'san francisco', 'indianapolis',
                    'columbus', 'fort worth', 'charlotte', 'detroit', 'el paso', 'seattle', 'denver', 'washington dc',
                    'memphis', 'boston', 'nashville', 'baltimore', 'portland','brooklyn']
                    
    if(cuisine_type != None and validate_cuisine(cuisine_type) != True):
        return build_validation_result(False,'Cuisine','We do not provide support for {} cuisine yet. Would you like to try some different cuisine from {}?'.format(cuisine_type,cuisine_types))

    if(city != None and validate_city(city) != True):
        return build_validation_result(False,'Location','We do not provide support in {} yet. Would you like to make a reservation in a different city?'.format(city))
        
    if(contact != None and validate_contact(contact) != True):
        return build_validation_result(False,'Contact','Please enter a valid Contact Number')
        
    if date != None:
        if(validate_date(date) != True):
            return build_validation_result(False,'Date','I cannot understand the date. For which date would you like to book a reservation?')
        elif(datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today()):
            return build_validation_result(False,'Date','You cannot make reservation for a previous date. Please enter a valid date.')

    return build_validation_result(True,None,None)

def make_reservation(intent_request):
    slots = intent_request['currentIntent']['slots']
    
    cuisine_type = slots['Cuisine']
    city = slots['Location']
    date = slots['Date']
    contact = slots['Contact']
    peopleCount = slots['PeopleCount']
    time = slots['Time']
    
    if intent_request['invocationSource'] == 'DialogCodeHook':
        result = validate_userDetails(cuisine_type, city, date, contact)
        
        if result['isValid'] != True:
            slots[result['violatedSlot']] = None
            return {
                    'sessionAttributes' : intent_request['sessionAttributes'],
                    'dialogAction': {
                            'type' : 'ElicitSlot',
                            'intentName' : intent_request['currentIntent']['name'],
                            'slots' : slots,
                            'slotToElicit' : result['violatedSlot'],
                            'message' : result['message']
                    }
            }
            
        return {
                'sessionAttributes' : intent_request['sessionAttributes'],
                'dialogAction' : {
                        'type' : 'Delegate',
                        'slots' : slots
                }
        }
    
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName = 'userRequestsQueue')
    response = queue.send_message(MessageBody = json.dumps(slots))
    logger.debug("Send result %s", response)
    print(type(contact))
       
    return {
        'sessionAttributes' : intent_request['sessionAttributes'],
        'dialogAction' : {
                'type' : 'Close',
                'fulfillmentState': 'Fulfilled',
                'message': {
                    'contentType': 'PlainText',
                    'content': 'You’re all set. Expect my recommendations shortly! Have a good day.'
             }
        }
    }

def lambda_handler(event, context):
    intent_name  = event['currentIntent']['name']
    
    if(intent_name == 'greeterIntent'):
        return {
            'sessionAttributes' : event['sessionAttributes'],
            'dialogAction' : {
                'type' : 'Close',
                'fulfillmentState': 'Fulfilled',
                'message': {
                    'contentType': 'PlainText',
                    'content': 'Hi there, how can I help you?'
             }
        }
    }
    if(intent_name == 'DiningSuggestionsIntent'):
        return make_reservation(event)