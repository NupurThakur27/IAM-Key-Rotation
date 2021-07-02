from util import *
import sys
from botocore.exceptions import ClientError

def send_deactivate_email(username, email_to, age, access_key_id):
    DELETION_DATE=datetime.datetime.today() + datetime.timedelta(15)
    emailmsg =DEACTIVATION_EMAIL_MESSAGE % (access_key_id, username, age,DELETION_DATE.strftime("%d %b %Y, %A"))
    emailsubject = 'AWS IAM Access Key Rotation - Deactivation of Access Key: %s' % access_key_id
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

def deactive_key(uname):
    try:
        username=uname
        print("Hello Username:", uname)
        client = boto3.client('iam', region_name=AWS_DEFAULT_REGION)
        access_keys = client.list_access_keys(UserName=username)['AccessKeyMetadata']
        tags = client.list_user_tags(UserName=username)['Tags']
        email = get_email(tags)
        user_keys = []

        for access_key in access_keys:
            access_key_id = access_key['AccessKeyId']
            masked_access_key_id = mask_access_key(access_key_id)
            print(masked_access_key_id)
            existing_key_status = access_key['Status']
            key_created_date = access_key['CreateDate']
            age = key_age(key_created_date)
            key_state = ''
            key_state_changed = False
            if age < KEY_MAX_DEACTIVATE_AGE_IN_DAYS:
                key_state = KEY_YOUNG_MESSAGE
                print("Based on Age",key_state)
            elif age >= KEY_MAX_DEACTIVATE_AGE_IN_DAYS:
                if existing_key_status == KEY_STATE_ACTIVE:
                    key_state = KEY_DEACTIVATED_MESSAGE
                    print("Active or Inactive ",key_state)
                    client.update_access_key(UserName=username, AccessKeyId=access_key_id, Status=KEY_STATE_INACTIVE)
                    if email == '':
                        print("Deactivate: Unable to find Email Tag for the IAM User")
                    else :
                        slack_message = DEACTIVATION_SLACK_MESSAGE%(masked_access_key_id, username)
                        print(slack_message)
                        send_slack_notification(slack_message,HOOK_URL)
                        send_deactivate_email(username, email, age, masked_access_key_id)
                    key_state_changed = True
                key_info = {'accesskeyid': masked_access_key_id, 'age': age, 'state': key_state, 'changed': key_state_changed}
                user_keys.append(key_info)   
        status = {'username': username, 'keys': user_keys}   
        print(status)      
        return  
    except ClientError as e:
        print (e)


def main():
    deactive_key(sys.argv[1])

if __name__ == "__main__" :
    main()