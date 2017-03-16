import boto3

def create():
    dynamo=boto3.client('dynamodb')
    response = dynamo.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'fbid',
                'AttributeType': 'S'
            }
        ],
        TableName='s3pic',
        KeySchema=[
            {
                'AttributeName': 'fbid',
                'KeyType': 'HASH'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return response['TableDescription']['TableName']