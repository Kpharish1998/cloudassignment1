import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3
import json
import re
import requests
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

client = boto3.client('lambda') #to communicate to lambda2


def slots(Req):
    return Req['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):  #this should go back to lex
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message,
            #'slots': slots
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }




def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')

def BuildResult(is_valid, violated_slot, message_content):
#goes back and gives details of violated slot and then transfered to elicit function back to lex
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



def validateOrder(cuisine_type, location, dining_time, num_people, email, date):

    #we are making a cuisine_types and location_list list by getting all the values from dynamodb, I have just copy pasted this list from my local computer after runnig the code

    
    cuisine_types = ['newamerican', 'latin', 'cocktailbars', 'mexican', 'hotdogs', 'cafes', 'himalayan', 'seafood', 'mediterranean', 'pizza', 'comfortfood', 'bars', 'modern_european', 'french', 'peruvian', 'tapasmallplates', 'chinese', 'burgers', 'caribbean', 'italian', 'thai', 'noodles', 'hotpot', 'coffee', 'breakfast_brunch', 'korean', 'bbq', 'bakeries', 'pubs', 'filipino', 'vietnamese', 'georgian', 'southern', 'lebanese', 'shanghainese', 'german', 'buffets', 'asianfusion', 'tex-mex', 'ramen', 'sandwiches', 'sushi', 'vegetarian', 'laotian', 'ethiopian', 'australian', 'gastropubs', 'belgian', 'restaurants', 'spanish', 'japanese', 'desserts', 'foodstands', 'wine_bars', 'delis', 'tradamerican', 'chickenshop', 'cuban', 'bagels', 'taiwanese', 'indpak', 'vegan', 'izakaya', 'food_court', 'lounges', 'persian', 'bookstores', 'hkcafe', 'tuscan', 'speakeasies', 'tapas', 'turkish', 'irish_pubs', 'teppanyaki', 'grocery', 'streetvendors', 'halal', 'malaysian', 'brazilian', 'seafoodmarkets', 'mideastern', 'venues', 'scandinavian', 'soulfood', 'burmese', 'tea', 'szechuan', 'dimsum', 'media', 'cajun', 'greek', 'hawaiian', 'foodtrucks', 'senegalese', 'steak', 'cantonese', 'puertorican', 'hungarian', 'haitian', 'chicken_wings', 'polish', 'japacurry', 'tacos', 'fooddeliveryservices', 'newmexican', 'african', 'argentine', 'culturalcenter', 'dominican', 'beergardens', 'cheese', 'austrian', 'wraps', 'pastashops', 'fondue', 'venezuelan', 'jazzandblues', 'creperies', 'conveyorsushi', 'hotels', 'diners', 'juicebars', 'brasseries', 'divebars', 'hainan']
    
    location_list = ['new york', 'brooklyn', 'maspeth', 'long island city', 'bayonne', 'ridgewood', 'hoboken', 'manhattan', 'astoria', 'elmhurst', 'jersey city', 'queens', 'weehawken', 'ny', 'glendale', 'sunnyside', 'jackson heights', 'bushwick', 'new york city', 'bedford-stuyvesant']

    if cuisine_type is not None and cuisine_type.lower() not in cuisine_types:
        return BuildResult(False,
                                       'Cuisine' ,
                                       'We don't have {} foods, do you like a different type of cuisine?'.format(cuisine_type))

    if location is not None and location.lower() not in location_list:
        print(location)
        
       
        return BuildResult(False,
                                       'Location' ,
                                       'Please enter an area within NYC or nearby')
                                        
        
    if date is not None:
        if not isvalid_date(date): 
            

            
            return BuildResult(False,'Date' , 'Could you type in proper date format?')
                                       
        elif datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today(): 
            
            return BuildResult(False, 'Date',  'Sorry, this day ain't possible, could you suggest another one?')

    if dining_time is not None: 
        if len(dining_time) != 5:
        
            return BuildResult(False, 'DiningTime', 'Please enter a valid time (AM/PM)')

        hour, minute = dining_time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return BuildResult(False, 'DiningTime', 'Please enter a valid time (AM/PM)')

    
    if num_people is not None:
        num_people = parse_int(num_people)
        
        if(math.isnan(num_people)):
            return BuildResult(False,
                                          'NumPeople' ,
                                       'Please type proper query')
            
            
        if num_people < 0 or num_people > 20:
            return BuildResult(False,
                                       'NumPeople' ,
                                       'Sorry! We accept reservations only upto 30 people')
            #return BuildResult(False, 'NumPeople', 'We accept reservations only upto 30 people')
                                        
        

    if email is not None:

        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            return BuildResult(False, 'EmailId', 'Please enter a valid e-mail.')

    return BuildResult(True, None, None)


""" --- Functions that control the bot's behavior --- """


def food_order(Req):

    print("foodorder")
    cuisine_type = slots(Req)["Cuisine"]
    location = slots(Req)["Location"]
    dining_time = slots(Req)["DiningTime"]
    num_people = slots(Req)["NumPeople"]
    email = slots(Req)["EmailId"]
    date= slots(Req)["Date"]

    

    print(Req['invocationSource'])
    
    
    if Req['invocationSource'] == 'DialogCodeHook':   #inorder for lex to send DialogCodeHook as invocation source, we have to gove permissions to lex to do, otheriwse its gonna be only fullfillmentcodehook

       
        slots = slots(Req)
        
        print("DialogCodeHook")
        validation_result = validateOrder(cuisine_type, location, dining_time, num_people, email, date)

#after validation, we are checking if any slot entries are violated, if yes, then we call elicit function to ask user to put proper slot values

        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(Req['sessionAttributes'],
                               Req['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        
        output_session_attributes = Req['sessionAttributes'] if Req['sessionAttributes'] is not None else {}
        return delegate(output_session_attributes, slots(Req))
        
    elif source == 'FulfillmentCodeHook':
        
        
        #now all slots are right and filled, we prepare to send the message object to lambda2
        
        
        
   
        slots = slots(Req)
        #message = {"message":"hello from lambda1"}
    
        response = client.invoke(
            
            FunctionName = 'arn:aws:lambda:us-east-1:713647610890:function:lambda2',
            InvocationType = 'RequestResponse',
            Payload = json.dumps(slots)
        )
        
       
    
        return close(Req['sessionAttributes'],'Fulfilled',
                     {'contentType': 'PlainText',
                      'content': 'Thanks, you can expectt suggestions shortly'})





def dispatch(Req):
    
#checking if right intent comes, since only DiningSuggestionsIntent invokes lf1, we dont check for other intents
    print("dispatch")
    logger.debug('dispatch userId={}, intentName={}'.format(Req['userId'], Req['currentIntent']['name']))

    intent_name = Req['currentIntent']['name']

  
    if intent_name == 'DiningSuggestionsIntent':
        return food_order(Req)

    raise Exception('Intent with name ' + intent_name + ' not supported')





def lambda_handler(event, context):
   
  
        
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    
    #print(event['sessionAttributes']) 
    print(event)
    return dispatch(event)

