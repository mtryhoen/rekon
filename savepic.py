import boto3
import dynamo

def s3save(memberid, membername, memberlastname, target_bytes):
    s3=boto3.client('s3')
    response = s3.put_object(
        Body=target_bytes,
        Bucket='string',
        Key=memberid,
    )
    
    dynsave(memberid, membername, memberlastname,)
def dynsave(memberid, membername, memberlastname,):