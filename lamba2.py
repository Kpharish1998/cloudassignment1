

import os
import subprocess 
import random

import json
import requests 
import boto3
 
from aws_requests_auth.aws_auth import AWSRequestsAuth


def BusinessIds(cuisine_type):
    
#we need to import a arn layer to give lambda the permission to recognize aws_requests_auth.aws, after that we get data from elastic search
    
    auth = AWSRequestsAuth(aws_access_key='',
                       aws_secret_access_key='',
                       aws_host='search-restaurants-elastic-draft1-gjjwdgrv3qb3yw7lorokbrz4.us-east-1.es.amazonaws.com',
                       aws_region='us-east-1',
                       aws_service='es')

    response = requests.get('https://search-restaurants-elastic-draft1-gjjwdgrv3qb3yw7lorokbrz4.us-east-1.es.amazonaws.com/_search?q='+str(cuisine_type),
                            auth=auth)

   
    
    res = response.json()
    
   
    hits = res['hits']['hits']
    
    buisinessIds = []

    for hit in hits:
        buisinessIds.append(str(hit['_source']['RestaurantID']))
    
    print(buisinessIds)
    return buisinessIds

def RestaurantsfromDynamo(restaurantIds):

#we get remaining data from dynamodb

    res = []
   

    client = boto3.client('dynamodb')
    for id in restaurantIds:
     
        response = client.get_item(TableName='Restaurants_Draft2', Key={'businessId':{'S':str(id)}})

	  if response['Item']['city']['S'].lower() == loc:          #filtering based on loc

            res.append(response)
        

    return res


def Message(restaurantDeets,message):

#scraping data and forming a msg to be sent as notifiaction

    if len(restaurantDeets) ==0:
        
        return "no availability of the cuisine you requested at these places"
        
    elif len(restaurantDeets) ==1:
        
        People = message['NumPeople']
        date = message['Date']
        time = message['DiningTime']
        cuisine = message['Cuisine']
        separator = ', '
        First = restaurantDeets[0]['Item']['name']["S"]
        FirstAddress = restaurantDeets[0]['Item']['address']["S"]
       
        msg = 'Hello! Here are my {0} restaurant suggestions for {1} people at {2} on {3} : 1. {4}, located at {5}. Enjoy your meal!'.format(cuisine,People,time,date,First,FirstAddress)
        print(msg)
        return msg    
        
    elif len(restaurantDeets) ==2:
        
        People = message['NumPeople']
        date = message['Date']
        time = message['DiningTime']
        cuisine = message['Cuisine']
        separator = ', '
        First = restaurantDeets[0]['Item']['name']["S"]
        FirstAddress = restaurantDeets[0]['Item']['address']["S"]
       Second = restaurantDeets[1]['Item']['name']["S"]
        SecondAddress = restaurantDeets[1]['Item']['address']["S"]
       
        msg = 'Hello! Here are my {0} restaurant suggestions for {1} people at {2} on {3} : 1. {4}, located at {5}, 2. {6}, located at {7}. Enjoy your meal!'.format(cuisine,People,time,date,First,FirstAddress,resTwoName,SecondAddress)
        print(msg)
        return msg    



def lambda_handler(event, context):
   
    cuisine = event['Cuisine'].lower()
    loc = event['Location'].lower()

    print(cuisine)

    businessIds=BusinessIds(cuisine)

    

    restaurantDeets = RestaurantsfromDynamo(businessIds, loc)

    print(restaurantDeets)

    if len(restaurantDeets) ==0:
        
        msg = Message([],event)
        print(msgToSend) 
        
    elif len(restaurantDeets)>1:
        
        details = random.sample(restaurantDeets, 2)
        
        msg = Message(details,event)
        
    elif len(restaurantDeets)==1:
        
         msg = Message(restaurantDeets,event) 
	

   
    print(msg)