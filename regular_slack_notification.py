#!/usr/bin/python3
import boto3
from base64 import b64decode
from util import *

decoded_url = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_HOOK_URL))['Plaintext'].decode('utf-8')
HOOK_URL = "https://" + decoded_url

def get_user_old_keys( keyAge ):
    client = boto3.client('iam',region_name = AWS_DEFAULT_REGION)
    usersList=client.list_users()

    timeLimit=datetime.datetime.now() - datetime.timedelta( days = keyAge)
    usrsWithOldKeys = {'Users':[],'Description':'List of users with Key Age greater than (>=) {} days'.format(keyAge),'KeyAgeCutOff':keyAge}

    # Iterate through list of users and compare with `key_age` to flag old key owners
    for k in usersList['Users']:
        accessKeys=client.list_access_keys(UserName=k['UserName'])
        # # Iterate for all users
        for key in accessKeys['AccessKeyMetadata']:
            if key['CreateDate'].date() <= timeLimit.date() and key['Status'] == 'Active':
                usrsWithOldKeys['Users'].append({ 'UserName': k['UserName'], 'KeyAgeInDays': (datetime.date.today() - key['CreateDate'].date()).days })
                
        # If no users found with older keys, add message in response
        if not usrsWithOldKeys['Users']:
            usrsWithOldKeys['OldKeyCount'] = 'Found 0 Key(s) that are older than {} days'.format(keyAge)
        else:
            usrsWithOldKeys['OldKeyCount'] = 'Found {0} Active Key(s) that are older than {1} days'.format(len(usrsWithOldKeys['Users']), keyAge)
        
    slack_message='Attention Required for the following IAM User(s):'
    user_details=''
    for users in usrsWithOldKeys['Users']:
        tags = client.list_user_tags(UserName=users['UserName'])['Tags']
        user_details += "\n \u2022 Username: `%s` KeyAge: `%s days`\n" % (users['UserName'],users['KeyAgeInDays'])
        if account_type(tags).lower() == 'Human'.lower(): 
            print(users['UserName'])
    if user_details != '':
        slack_message = slack_message + user_details
        send_slack_notification(slack_message,HOOK_URL)
    return

def main():
    get_user_old_keys(EXPIRY_KEY_AGE_NOTIFICATION)

if __name__ == "__main__" :
    main()
