import boto3
import json
import urllib.request as urllib2
import urllib.parse as urllib
import io
import requests
import unicodedata

    resp = urllib2.urlopen(url).read().decode('utf-8')
    # convert the returned JSON string to a Python datatype
    members = json.loads(resp)
    for member in members['data']:
        MEMID[member['id']] = member['name']


