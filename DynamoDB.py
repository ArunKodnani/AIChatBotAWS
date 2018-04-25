import json
import boto3
import requests
import time
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import csv

from urllib.parse import quote

API_KEY = 'xIAAbGzxOp6qTgHBDqR9P56Wa30cKLFE1r8r4QGntKGsyR2K0iOqj5KWU1R874mC1R6HmirA9C7AtfcseOo0_6IrZkfa8SNqbzKK0gJMwyDmv56uHjuzXXDcbLm-WnYx'

API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'



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


def search(api_key, term, location, offset, limit):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
        offset(int): Current Set of records.
    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'offset': offset,
        'limit': limit
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


def query_api(term, location, offset, limit):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
        offset(int): Current Set of records.
    """
    response = search(API_KEY, term, location, offset, limit)

    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, location))
        return
    return businesses

def getDataFromYelp(term, table):
    offset = 0
    while(offset<1000):
        businesses = query_api(term, "Manhattan", offset, 50)
        offset = offset + 50
        if businesses:
            for business in businesses:
                business['insertedAtTimestamp'] = time.time()
                response = table.query(
                    KeyConditionExpression=Key('id').eq(business['id'])
                )
                items = response['Items']
                if not items:
                    f = open("/Users/arunkodnani/GoogleDrive/MSCS/Cloud Computing/Assignment3/File1.csv", 'a')
                    file1List = [business['id'], business['review_count'], business['rating'], term.split(" ")[0]]
                    with f:
                        writer = csv.writer(f)
                        writer.writerow(file1List)
                        f.flush()
                    f.close()
                    x = json.loads(json.dumps(business).replace("\"\"", "\"null\""), parse_float=Decimal)
                    table.put_item(
                        Item=x
                    )
        else:
            offset = 1000


if __name__ == '__main__':

    # Creating DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name = 'us-east-2')

    # Creating table yelp-restaurants
    table = dynamodb.create_table(
        TableName='yelp-restaurants',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'insertedAtTimestamp',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'insertedAtTimestamp',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    # Adding 10 second delay to avoid insertion into table before creation.
    time.sleep(10)

    getDataFromYelp("chinese restaurants", table)
    getDataFromYelp("indian restaurants", table)
    getDataFromYelp("thai restaurants", table)
    getDataFromYelp("mexican restaurants", table)
    getDataFromYelp("italian restaurants", table)
    getDataFromYelp("japanese restaurants", table)
    getDataFromYelp("french restaurants", table)
    getDataFromYelp("greek restaurants", table)
    getDataFromYelp("cajun restaurants", table)