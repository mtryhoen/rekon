import boto3

rekognition = boto3.client('rekognition', region_name='eu-west-1')
s3con = boto3.client('s3', region_name='eu-west-1')

def update_col(COLLECTION, bucket, prefix):

    collections = rekognition.list_collections().get('CollectionIds', [])
    if COLLECTION not in collections:
        print("Creating Collection " + COLLECTION)
        response = rekognition.create_collection(
            CollectionId=COLLECTION
        )
    else:
        print("Collection " + COLLECTION + " already exists, cleaning")
        response = rekognition.delete_collection(
            CollectionId=COLLECTION
        )
        response = rekognition.create_collection(
            CollectionId=COLLECTION
        )

    istrunk=1
    marker=''
    while istrunk:
        objects = s3con.list_objects(Bucket=bucket, Prefix=prefix, Marker=marker)
        photos = objects.get('Contents')
        marker = objects.get('NextMarker')
        print(bucket)
        print(photos)

        for photo in photos:
            imgname = photo['Key'].split("/")[2].split(".")[0]
            imgkey = photo['Key']
            response = rekognition.index_faces(
                CollectionId=COLLECTION,
                Image={
                    #'Bytes': target_bytes
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': imgkey
                    }
                },
                ExternalImageId=imgname
            )
        istrunk = objects.get('IsTruncated')


# --------------- Main handler ------------------

def lambda_handler(event, context):
    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    user, COLLECTION, photo = key.split('/')
    collectionName = user + "-" + COLLECTION
    prefix = user + "/" + COLLECTION + "/"

    try:

        # Calls Amazon Rekognition IndexFaces API to detect faces in S3 object
        # to index faces into specified collection

        response = update_col(collectionName, bucket, prefix)

    except Exception as e:
        print(e)
        print("Error updating collection {}. ".format(COLLECTION))
        raise e
