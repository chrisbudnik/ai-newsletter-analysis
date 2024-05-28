import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

class GmailHandler:
    """
    Gmail API Handler. Interacts with Gmail API.
    """
    def __init__(self, credential_path, token_path='token.json', scopes=None):
        self.credential_path = credential_path
        self.token_path = token_path
        self.scopes = scopes or ['https://www.googleapis.com/auth/gmail.readonly']
        self.service = self.authenticate_gmail()

    def authenticate_gmail(self):
        """
        Authenticate to Gmail API. If available, use the token file to authenticate.
        Otherwise, create a new token file with the oauth flow credentials.
        """
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credential_path, self.scopes)
                creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        return build('gmail', 'v1', credentials=creds)
    

    def list_messages(
            self, user_id: str = 'me', query: str = '', max_results: int = 10
        ) -> list[dict]:

        try:
            response = self.service.users().messages().list(userId=user_id, q=query, maxResults=max_results).execute()
            messages = response.get('messages', [])
            return messages
        
        except HttpError as error:
            print(f'An error occurred: {error}')
            return

    def get_message(self, user_id, msg_id):
        try:
            message = self.service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
            msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII')).decode('utf-8')
            return msg_str
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def parse_message(self, raw_message):
        # This function can be customized to parse the email's content as needed
        pass

# Example usage
def main():
    gmail = GmailHandler('credentials.json')
    messages = gmail.list_messages(query='is:unread')
    if messages:
        for msg in messages:
            content = gmail.get_message('me', msg['id'])
            # Now parse or process the content as needed
            print(content)

if __name__ == '__main__':
    main()
