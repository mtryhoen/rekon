import boto3
import io
from PIL import Image

rekognition = boto3.client('rekognition', region_name='eu-west-1')
s3con = boto3.client('s3', region_name='eu-west-1')

def get_public_url(bucket, key):
    bucket_location = s3con.get_bucket_location(Bucket=bucket)
    object_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
        bucket_location['LocationConstraint'],
        bucket,
        key)
    return object_url

def tag_image(bucket, key, index, faceid, similarity):
    response = s3con.put_object_tagging(
        Bucket=bucket,
        Key=key,
        Tagging={
            'TagSet': [
                {
                    'Key': str(index) + '-' + str(similarity),
                    'Value': str(faceid)
                },
            ]
        }
    )

def get_image(bucket, key):
    # download image locally
    s3 = boto3.resource('s3')
    s3.meta.client.download_file(bucket, key, '/tmp/image.jpg')

def get_collection(bucket, key):
    # get object tags
    response = s3con.get_object_tagging(
        Bucket=bucket,
        Key=key
    )
    Tags = response['TagSet']
    for tag in Tags:
        if tag['Key'] == 'collection':
            return tag['Value']

def detect_faces(bucket, key):
    get_image(bucket, key)
    prefix, id = key.split('/')
    collection = get_collection(bucket, key)
    collectionid = prefix + '-' + collection
    response = rekognition.detect_faces(
        Image={
            "S3Object": {
                "Bucket": bucket,
                "Name": key

            }
        },
    )
    all_faces = response['FaceDetails']

    # Initialize list object
    boxes = []

    # Get image diameters
    image = Image.open("/tmp/image.jpg")
    image_width = image.size[0]
    image_height = image.size[1]

    # Crop face from image
    for face in all_faces:
        box = face['BoundingBox']
        x1 = int(box['Left'] * image_width) * 0.9
        y1 = int(box['Top'] * image_height) * 0.9
        x2 = int(box['Left'] * image_width + box['Width'] * image_width) * 1.10
        y2 = int(box['Top'] * image_height + box['Height'] * image_height) * 1.10
        image_crop = image.crop((x1, y1, x2, y2))

        stream = io.BytesIO()
        image_crop.save(stream, format="JPEG")
        image_crop_binary = stream.getvalue()

        # Submit individually cropped image to Amazon Rekognition
        response = rekognition.search_faces_by_image(
            CollectionId=collectionid,
            Image={'Bytes': image_crop_binary}
        )

        if len(response['FaceMatches']) > 0:
            # Return results
            i = 1
            for match in response['FaceMatches']:
                print(match['Face']['ExternalImageId'])
                print(match['Similarity'])
                tag_image(bucket, key, i, match['Face']['ExternalImageId'], match['Similarity'])
                i = i+1
            return 0
        else:
            print('no face detected')
            return 1

# --------------- Main handler ------------------

def lambda_handler(event, context):
    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    # key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    key = event['Records'][0]['s3']['object']['key']

    try:

        # Calls Amazon Rekognition IndexFaces API to detect faces in S3 object
        # to index faces into specified collection

        detection = detect_faces(bucket, key)
        if detection == 0:
            public_url = get_public_url(bucket, key)
            snscon = boto3.client('sns')
            response = snscon.publish(
                TopicArn='arn:aws:sns:eu-west-1:019179343942:rekon',
                Message='A face was detected:' + str(public_url),
                Subject='rekon alert',
            )
        else:
            s3con.delete_object(
                Bucket=bucket,
                Key=key
            )


    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket))
        raise e
