import base64
import os
import re
import pandas as pd
from googleapiclient.discovery import build
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

    def list_messages(self, user_id: str = "me", max_results: int = 10) -> list[dict]:
        """List the last 'max_results' messages of the user's mailbox."""

        response = self.service.users().messages().list(userId=user_id, maxResults=max_results).execute()
        messages = response.get('messages', [])
        return messages

    def all_headers(self, msg_id, user_id: str = "me") -> dict:
        """Get all the headers of a single message."""

        message = self.service.users().messages().get(userId=user_id, id=msg_id, format='metadata').execute()
        headers = message.get('payload', {}).get('headers', [])
        return {header['name']: header['value'] for header in headers}

    def headers(self, msg_id, user_id: str = "me", selected_headers: list = ['Subject', 'From', 'Date']) -> dict:
        """Get selected the headers of a single message."""
        
        headers = self.all_headers(msg_id, user_id)
        try:
            output = {header: headers[header] for header in selected_headers}
        except KeyError:
            raise KeyError(f"At least one of selected headers not found in message: {headers.keys()}")
        
        return output

    def text_body(self, msg_id, user_id: str = "me"):
        """Get the body of a single message."""

        message = self.service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        data = message['payload']['parts'][0]['body']['data']
        return self._decode_and_transform_text(data)
    
    def html_body(self, msg_id, user_id: str = "me"):
        """Get the body of a single message."""

        message = self.service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        data = message['payload']['parts'][1]['body']['data']
        return self._decode_and_transform_text(data)
    
    def parts(self, msg_id, user_id: str = "me"):
        """Get parts of a single message."""

        message = self.service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        data = message['payload']['parts']
        return data
    
    @staticmethod
    def _decode_and_transform_text(msg: str) -> str:
        """Parse text/plain message."""

        # Decoding from base64 URL-safe encoded string
        msg = base64.urlsafe_b64decode(msg).decode('utf-8')

        # Remove '\r\n' from the message
        msg = msg.replace('\r\n', '\n')

        # Remove html-specific characters from the message
        msg = re.sub(r'[\xa0\u200c]', '', msg)
        
        return msg



