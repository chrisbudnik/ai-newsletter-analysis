import base64
import os
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def gmail_authenticate():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def list_messages(service, user_id):
    # List all messages of the user's mailbox.
    response = service.users().messages().list(userId=user_id).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])
    return messages

def get_message(service, user_id, msg_id):
    # Get a single message.
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    return message

def main():
    service = gmail_authenticate()
    messages = list_messages(service, 'me')
    
    emails = []
    for message in messages:
        msg = get_message(service, 'me', message['id'])
        # Here you need to parse the msg and extract the desired info
        # For example, headers, sender, and content
        # Add the extracted info to the emails list

    df = pd.DataFrame(emails, columns=['Header', 'Sender', 'Content'])
    print(df)

if __name__ == '__main__':
    main()
