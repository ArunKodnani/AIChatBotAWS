from botocore.vendored import requests
import time
from datetime import datetime
import boto3
from urllib.parse import quote
import json
from boto3.dynamodb.conditions import Key,Attr

API_KEY = 'xIAAbGzxOp6qTgHBDqR9P56Wa30cKLFE1r8r4QGntKGsyR2K0iOqj5KWU1R874mC1R6HmirA9C7AtfcseOo0_6IrZkfa8SNqbzKK0gJMwyDmv56uHjuzXXDcbLm-WnYx'

API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'

OPEN_AT = time.time()
SEARCH_LIMIT = 3
url = 'https://search-chatbotdomain-a4foblwyclavfcvwdnwaaqucjq.us-east-1.es.amazonaws.com/restaurants/_search'
dynamodb = boto3.resource('dynamodb',region_name='us-east-2')
table = dynamodb.Table('yelp-restaurants')



def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)
    return response.json()


def search(api_key, term, location, openAt, sort_by):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
        openAt (unix time epoch): The time at which a particular place will be open.
    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'open_at': openAt,
        'sort_by': sort_by,
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


def query_api(term, location, openAt, sort_by):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
        openAt (unix time epoch): The time at which a particular place will be open.
    """
    response = search(API_KEY, term, location, openAt, sort_by)

    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, location))
        return
    return businesses




def lambda_handler(event, context):
    
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName = 'userRequestsQueue')
    # testcui = 'Indian'
    # payload = {'q': testcui}
    # response  = requests.get(url,payload)
    # dict = response.json()
    # for element in dict['hits']['hits']:
    #     id = element['_source']['RestaurantID']
    #     dynamoResponse = table.query(KeyConditionExpression=Key('id').eq(id))
    #     restaurant_location = dynamoResponse['Items'][0]['location']['display_address'][0]+ dynamoResponse['Items'][0]['location']['display_address'][1]
    #     restaurant_name = dynamoResponse['Items'][0]['name']
    #     print(restaurant_location)
    #     print(restaurant_name)
    # print(response.json())
  
    
    
    for message in queue.receive_messages():
        tempMessage = message
        userData = json.loads(message.body)
        recommendations = []
        input_date = userData['Date']
        input_time = userData['Time']
        complete_date = datetime.strptime(input_date + " " + input_time, '%Y-%m-%d %H:%M')
        openAt = complete_date.timestamp()
        term = userData['Cuisine']
        location = userData['Location']
        contact = userData['Contact']
        sort_by = "rating"
        number_of_people = userData['PeopleCount']
        payload = {'q': term}
        response  = requests.get(url,payload)
        dict = response.json()
        for element in dict['hits']['hits']:
            id = element['_source']['RestaurantID']
            dynamoResponse = table.query(KeyConditionExpression=Key('id').eq(id))
            restaurant_location = dynamoResponse['Items'][0]['location']['display_address'][0]+ dynamoResponse['Items'][0]['location']['display_address'][1]
            restaurant_name = dynamoResponse['Items'][0]['name']
            print(restaurant_location)
            print(restaurant_name)
            recommendation = {}
            recommendation[0] = restaurant_name
            recommendation[1] = restaurant_location
            recommendations.append(recommendation)
    
    
        message = "Hello! Here are my {} restaurant suggestions for {} people, for {} at {}:\n".format(term, number_of_people, input_date,input_time)
        index = 1
        for recommendation in recommendations:
            message = message + "{}. {}, {}\n".format(index,recommendation[0], recommendation[1])
            index = index + 1
        message = message + "Enjoy your meal!"
        print(message)
        print("testing print")
        # TODO implement
        client = boto3.client('sns')
        response = client.publish(
            #TopicArn='string',
            #TargetArn='string',
            PhoneNumber=contact,
            Message= message,
            #Subject='string',
            MessageStructure='String'
            )
        
        if(response['ResponseMetadata']['HTTPStatusCode'] == 200):
            tempMessage.delete()
     
    return 'SNS sent'
