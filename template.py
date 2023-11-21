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

def list_messages(service, user_id, max_results=10):
    # List the last 'max_results' messages of the user's mailbox.
    response = service.users().messages().list(userId=user_id, maxResults=max_results).execute()
    messages = response.get('messages', [])
    return messages

def get_message_header(service, user_id, msg_id):
    # Get the headers of a single message.
    message = service.users().messages().get(userId=user_id, id=msg_id, format='metadata').execute()
    headers = message.get('payload', {}).get('headers', [])
    header_info = {}
    for header in headers:
        if header['name'] in ['Subject', 'From', 'Date']:
            header_info[header['name']] = header['value']
    return header_info

def main():
    service = gmail_authenticate()
    messages = list_messages(service, 'me')

    emails = []
    for message in messages:
        header_info = get_message_header(service, 'me', message['id'])
        emails.append(header_info)
    
    df = pd.DataFrame(emails)
    print(df)

if __name__ == '__main__':
    main()


