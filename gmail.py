import base64
import os
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailConnector:
    """Gmail API Connector. Interacts with Gmail API."""

    def __init__(self, path: str = 'token.json') -> None:
        self.path = path
        self.service = self._gmail_authenticate()

    def _gmail_authenticate(self):
        """Authenticate to Gmail API."""

        if not os.path.exists(self.path):
            raise EnvironmentError(f"Credentials file: {self.path} not found.")
            
        creds = Credentials.from_authorized_user_file(self.path, SCOPES)
        return build('gmail', 'v1', credentials=creds)

    def list_messages(self, user_id: str = "me", max_results: int = 10):
        """List the last 'max_results' messages of the user's mailbox."""

        response = self.service.users().messages().list(userId=user_id, maxResults=max_results).execute()
        messages = response.get('messages', [])
        return messages

    def get_message_header(self, msg_id, user_id: str = "me"):
        # Get the headers of a single message.
        message = self.service.users().messages().get(userId=user_id, id=msg_id, format='metadata').execute()
        headers = message.get('payload', {}).get('headers', [])
        header_info = {}
        for header in headers:
            if header['name'] in ['Subject', 'From', 'Date']:
                header_info[header['name']] = header['value']
        return header_info


if __name__ == '__main__':
    gmail = GmailConnector()
    messages = gmail.list_messages()

    emails = []
    for message in messages:
        header_info = gmail.get_message_header('me', message['id'])
        emails.append(header_info)
    
    df = pd.DataFrame(emails)
    print(df)


