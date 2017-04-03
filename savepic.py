import boto3
import dynamo

def s3save(memberid, target_bytes, BUCKET):
    s3=boto3.client('s3')
    response = s3.put_object(
        Body=target_bytes,
        Bucket=BUCKET,
        Key=memberid,
    )
    return response['']['']

def createdb(dynamo):

    response = dynamo.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'fbid',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 's3key',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'first_name',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'last_name',
                'AttributeType': 'S'
            }
        ],
        TableName='s3pic',
        KeySchema=[
            {
                'AttributeName': 'fbid',
                'KeyType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    return response['TableDescription']['TableName']

def addpicdb(dynamo, tablename, memberid, memberfirstname, memberlastname):
    table = dynamo.Table(tablename)
    with table.batch_writer() as batch:
        for i in range(50):
            batch.put_item(
                Item={
                    'fbid': memberid,
                    's3key': 'rekon-fbpics/' + memberid,
                    'first_name': memberfirstname,
                    'last_name': memberlastname
                }
            )