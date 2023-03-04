import json
import datetime
import boto3

def lambda_handler(event, context):
     
    print(event)
    
    userMessage = event["messages"][0]["unstructured"]["text"]
    client = boto3.client("lex-runtime")
    
    response = client.post_text(
        botName="MyBot",             #mentioning my lexbot's name and its alias and the lambda's name
        botAlias="Test",
        userId="lamda0",
        inputText=userMessage
    );
    
    UnstructuredMessage = {
        "id" : "0",
        "text" : response["message"],
        "timestamp" : str(datetime.datetime.now())
    }
    
    Message = {
        "type" : "string",
        "unstructured" : UnstructuredMessage
    }
    
    botResponse = {
        "messages": [Message]
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(botResponse)
    }
    
