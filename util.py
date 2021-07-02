import requests, json
import datetime, boto3
from base64 import b64decode

AWS_EMAIL_REGION = 'us-east-1'
AWS_DEFAULT_REGION = 'ap-southeast-1'
KEY_YOUNG_MESSAGE = 'Key is still young'
KEY_DEACTIVATED_MESSAGE = 'key is now EXPIRED! Changing key to INACTIVE state'
KEY_DELETED_MESSAGE = 'Key is now deleted'
WARNING_MESSAGE = 'Key is about to expire, send warning'

MASK_ACCESS_KEY_LENGTH = 15
ACCESS_KEY_LENGTH = 20
KEY_STATE_ACTIVE = "Active"
KEY_STATE_INACTIVE = "Inactive"

EXPIRY_KEY_AGE_NOTIFICATION = 42

ENCRYPTED_HOOK_URL = "AQICAHgQoY6rIhRRO3x7sKf4NyxyMPkGQVFWqCNi/+Dtcfv4SAHXVXrrn6Xar8cdHbgmFG5kAAAAqzCBqAYJKoZIhvcNAQcGoIGaMIGXAgEAMIGRBgkqhkiG9w0BBwEwHgYJYIZIAWUDBAEuMBEEDNwF/9SuCp+xvWG0PgIBEIBkBWFFrFwb9vjFO5ldImL8xF9equK50wZMc6H2dEKz/tUnmDE0W3cXuFWuTWFZfUYaqJwp+tJ0Zn6bI78OaLSnoVjXhqCslAYVUuTCxQsXApEf2nAfDnmInhTf85irFGXLuYO/vQ=="
decoded_url = boto3.client('kms', region_name=AWS_DEFAULT_REGION).decrypt(CiphertextBlob=b64decode(ENCRYPTED_HOOK_URL))['Plaintext'].decode('utf-8')
HOOK_URL = "https://" + decoded_url

KEY_MAX_DEACTIVATE_AGE_IN_DAYS = 45
KEY_MAX_DELETE_AGE_IN_DAYS = 60


EMAIL_FROM = 'tech@gather.network'
EMAIL_TO = ''


WARNING_EMAIL_MESSAGE="""Need immediate attention for the key [%s] associated with the user [%s] due to it being %s days old.

\u2022 Your key will expire after 3 days [%s].
\u2022 Your key will be deleted after 15 days [%s].

Please generate a new key for yourself.
"""

DEACTIVATION_EMAIL_MESSAGE= """The Access Key [%s] belonging to User [%s] has been automatically deactivated due to it being %s days old.
    
Access Key will be deleted after 15 days on [%s]

Please generate a new key for yourself.
"""
DEACTIVATION_SLACK_MESSAGE='Access Key `%s` belonging to `%s` deactivated.'

DELETION_EMAIL_MESSAGE=""""The Access Key [%s] belonging to User [%s] has been automatically deleted due to it being %s days old."""
DELETION_SLACK_MESSAGE='Access Key `%s` belonging to `%s` deleted.'
def mask_access_key(access_key):
    return access_key[-(ACCESS_KEY_LENGTH-MASK_ACCESS_KEY_LENGTH):].rjust(len(access_key), "*")

def get_email(tags):
    for tag in tags:
        if tag['Key'].lower() == 'Email'.lower():
            return tag['Value']
    return ''

def account_type(tags):
    for tag in tags:
        if tag['Key'].lower() == 'Account Type'.lower():
            return tag['Value']
    return ''


def key_age(key_created_date):
    tz_info = key_created_date.tzinfo
    age = datetime.datetime.now(tz_info) - key_created_date

    key_age_str = str(age)
    if 'days' not in key_age_str:
        return 0

    days = int(key_age_str.split(',')[0].split(' ')[0])

    return days

def send_slack_notification(slack_message, hook_url):
    slack_data = {'text': slack_message}
    response = requests.post(
    hook_url, data =json.dumps(slack_data),
    headers={'Content-Type': 'application/json'}
    )
    return response
