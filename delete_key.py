import boto3, sys
from botocore.exceptions import ClientError
from util import *

def send_delete_email(username, email_to, age, access_key_id):
    emailmsg = DELETION_EMAIL_MESSAGE % (access_key_id, username, age)
    emailsubject = 'AWS IAM Access Key Rotation - Deletion of Access Key: %s' % access_key_id
    client = boto3.client('ses',region_name=AWS_EMAIL_REGION)
    response = client.send_email(
        Source=EMAIL_FROM,
        Destination={
            'ToAddresses': [email_to]
        },
        Message={
            'Subject': {
                'Data': emailsubject
            },
            'Body': {
                'Text': {
                    'Data': emailmsg
                }
            }
        })
    return response

def delete_key(uname):
    try:
        username=uname
        client = boto3.client('iam', region_name=AWS_DEFAULT_REGION)
        access_keys = client.list_access_keys(UserName=username)['AccessKeyMetadata']
        tags = client.list_user_tags(UserName=username)['Tags']
        email = get_email(tags)
        user_keys = []

        for access_key in access_keys:
            access_key_id = access_key['AccessKeyId']
            masked_access_key_id = mask_access_key(access_key_id)
            existing_key_status = access_key['Status']
            key_created_date = access_key['CreateDate']
            age = key_age(key_created_date)

            key_state = ''
            key_state_changed = False
            if age < KEY_MAX_DELETE_AGE_IN_DAYS:
                key_state = KEY_YOUNG_MESSAGE
            elif age >= KEY_MAX_DELETE_AGE_IN_DAYS:
                key_state = KEY_DELETED_MESSAGE
                if existing_key_status == KEY_STATE_ACTIVE:
                    client.update_access_key(UserName=username, AccessKeyId=access_key_id, Status=KEY_STATE_INACTIVE)
                client.delete_access_key (UserName=username,AccessKeyId=access_key_id)
                if email == '':
                    print("Delete: Unable to find Email Tag for the IAM User")
                else :
                    slack_message = DELETION_SLACK_MESSAGE%(masked_access_key_id, username)
                    send_slack_notification(slack_message,HOOK_URL)
                    send_delete_email(username, email, age, masked_access_key_id)
                key_state_changed = True
            key_info = {'accesskeyid': masked_access_key_id, 'age': age, 'state': key_state, 'changed': key_state_changed}
            user_keys.append(key_info)   
        status = {'username': username, 'keys': user_keys}   
        print(status)      
        return            

    except ClientError as e:
        print (e)


def main():
    delete_key(sys.argv[1])

if __name__ == "__main__" :
    main()