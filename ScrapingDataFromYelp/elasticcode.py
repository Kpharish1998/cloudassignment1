import json
import boto3
import requests
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource('dynamodb', region_name='',aws_access_key_id='',aws_secret_access_key='')

table = dynamodb.Table('Restaurants_Draft2')

resp = table.scan()


while True:
    print(len(resp['Items']))
    
    for item in resp['Items']:
        ind="{\"index\" : { \"_index\": \"indexnew\", \"_id\" : \""+str(i)+"\" }}"
        body = "{\"RestaurantID\": \""+item['businessId']+"\", \"Cuisine\": \""+item['category']+"\"}"
        print(ind)
        print(body)

#so we basically create a dynamodb instance and access our dynamodb table name and access credentials and form the two strings called ind and body and print them, we then copy them into a text file and replace all single quotes with double quotes and converst this into ndjson format and use bulk ingestion curl command to add values into elastic search 

#the file added into elastic search containing the scrapped data is also in the folder named as:NDJSONELASTICSEARCHWORKING

        
