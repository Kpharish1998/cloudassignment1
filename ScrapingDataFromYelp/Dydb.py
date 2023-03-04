import boto3

#creation of table in dynamodb after configuring aws cli

client = boto3.client('dynamodb', region_name='us-east-1')

try:
    resp = client.create_table(
        TableName="Restaurants_Draft2",
       
        KeySchema=[
            {
                "AttributeName": "businessId",
                "KeyType": "HASH"
            }
        ],
      
        AttributeDefinitions=[
            {
                "AttributeName": "businessId",
                "AttributeType": "S"
            }
        ],
       
        ProvisionedThroughput={
            "ReadCapacityUnits": 1,
            "WriteCapacityUnits": 1
        }
    )
    print("Table created successfully!")
except Exception as e:
    print("Error creating table:")
    print(e)


#scraping data from yelp and adding it into dynamodb table by provinding yelp API and creating dynamodb table instance by specifying my table name

from botocore.exceptions import ClientError


dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table("Restaurants_Draft2")   #creation of table instance

import requests
import json
from decimal import Decimal
import datetime



# Defining keys, endpoints and headers
API_KEY = 'placing your yelp app api key after creating the app in its website'
ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
HEADERS = {'Authorization': 'bearer %s' % API_KEY}

#adding around 1000 restaurants after incrementing offset in each loop by 50, coz yelp allows around 50 pulls as maximum

for i in range(5):
    offset = 0
    for i in range(0, 19):
        offset += 50
        PARAMETERS = {
            'term': 'restaurant',
            'location': 'New York',
            'radius': 40000,                                         
            'limit': 50,
            'offset': offset,
            'sort_by': 'best_match'
        }

        response = requests.get(url=ENDPOINT, params=PARAMETERS, headers=HEADERS)

        data = response.json() #scrapped data in json format

        try:
            
            for i in data['businesses']:
                try:
                    table.put_item(              #table.put_item is used to create coloumn in dynamodb table with corresponding keys as the coloumn bame and values as the keys values, which we scrape from yelp

                        Item={
                            'businessId': i['id'],
                            'name': i['name'],
                            'category': i['categories'][0]['alias'],
                            'address': i['location']['address1'],
                            'city': i['location']['city'],
                            'zipcode': i['location']['zip_code'],
                            'latitude': Decimal(str(i['coordinates']['latitude'])),
                            'longitude': Decimal(str(i['coordinates']['longitude'])),
                            'reviewCount': i['review_count'],
                            'rating': Decimal(str(i['rating'])),
                            'phone': i['phone'],
                            'url': str(i['url']),
                            'insertedAtTimestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        },
                        ConditionExpression='attribute_not_exists(businessId) AND attribute_not_exists(insertedAtTimestamp)'
                    )
                except ClientError as e:
                    print(e.response['Error']['Code'])
        
        except ClientError as e:
                    print(e.response['Error']['Code'])
            
                