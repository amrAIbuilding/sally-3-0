"""
Sally 3.0 - Gmail API Connector
Connects to Gmail using your existing API credentials from Sally 1.0

EDUCATIONAL CONCEPTS:
- OAuth 2.0: Secure way to access Gmail without storing passwords
- API Rate Limiting: Respecting Gmail's usage limits  
- Error Handling: Graceful failures for network/authentication issues
- Data Extraction: Converting Gmail API responses to usable data
"""

import os
import pickle
import json
from pathlib import Path
from datetime import datetime, timedelta

# Gmail API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GmailConnector:
    """
    Handles all Gmail API operations for Sally 3.0
    Reuses your existing Gmail API credentials from Sally 1.0
    """
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.service = None
        self.credentials = None
        
        # Gmail API scopes - what permissions Sally needs
        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',    # Read emails
            'https://www.googleapis.com/auth/gmail.send',        # Send urgent alerts
            'https://www.googleapis.com/auth/gmail.modify'       # Mark emails as read/processed
        ]
        
        print("📧 GmailConnector initialized")
    
    def authenticate(self, client_secret_path="client_secret.json"):
        """
        Authenticate with Gmail using local file or environment variables
        """
        print(f"🔐 Authenticating with Gmail API...")
        
        # Check if we have stored credentials
        token_path = Path("token.json")
        
        try:
            # Try to load existing token
            if token_path.exists():
                print("   📱 Found existing token, loading...")
                self.credentials = Credentials.from_authorized_user_file(
                    token_path, self.SCOPES
                )
            
            # If there are no (valid) credentials available, let the user log in
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    print("   🔄 Refreshing expired credentials...")
                    self.credentials.refresh(Request())
                else:
                    print("   🆕 Need new authentication...")
                    
                    # Try environment variables first (for cloud deployment)
                    client_id = os.getenv('GMAIL_CLIENT_ID')
                    client_secret = os.getenv('GMAIL_CLIENT_SECRET')
                    
                    if client_id and client_secret:
                        print("   ☁️ Using environment variables for authentication")
                        # Create credentials from environment variables
                        client_config = {
                            "installed": {
                                "client_id": client_id,
                                "client_secret": client_secret,
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token",
                                "redirect_uris": ["http://localhost"]
                            }
                        }
                        
                        flow = InstalledAppFlow.from_client_config(
                            client_config, self.SCOPES
                        )
                        # For cloud environments, we can't open browser
                        print("   ⚠️ Cloud environment detected - manual authentication required")
                        return False
                        
                    else:
                        # Use local file (for development)
                        if not Path(client_secret_path).exists():
                            print(f"❌ Client secret file not found: {client_secret_path}")
                            print("   Please copy your Gmail API credentials file to the project root")
                            return False
                        
                        flow = InstalledAppFlow.from_client_secrets_file(
                            client_secret_path, self.SCOPES
                        )
                        self.credentials = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                if self.credentials:
                    with open(token_path, 'w') as token:
                        token.write(self.credentials.to_json())
                    print("   💾 Credentials saved for future use")
            
            # Build the Gmail service
            self.service = build('gmail', 'v1', credentials=self.credentials)
            print("✅ Gmail API authentication successful!")
            return True
        
    except Exception as e:
        print(f"❌ Gmail authentication failed: {str(e)}")
        return False
        
    def test_connection(self):
        """
        Test the Gmail connection by getting basic profile info
        """
        if not self.service:
            print("❌ Gmail service not initialized. Run authenticate() first.")
            return False
        
        try:
            print("🧪 Testing Gmail connection...")
            
            # Get user profile (safe, minimal data)
            profile = self.service.users().getProfile(userId='me').execute()
            email_address = profile.get('emailAddress')
            total_messages = profile.get('messagesTotal', 0)
            
            print(f"   ✅ Connected to: {email_address}")
            print(f"   📊 Total messages in account: {total_messages:,}")
            
            return True
            
        except HttpError as error:
            print(f"❌ Gmail connection test failed: {error}")
            return False
    
    def get_school_emails(self, days_back=7, max_results=100):
        """
        Fetch emails from configured school domains
        This is where Sally finds the school communications to analyze
        """
        if not self.service:
            print("❌ Gmail service not initialized. Run authenticate() first.")
            return []
        
        print(f"📬 Fetching school emails from last {days_back} days...")
        
        # Build search query for school domains
        school_domains = self.config.schools
        if not school_domains:
            print("⚠️ No school domains configured")
            return []
        
        # Create Gmail search query: "from:domain1.edu OR from:domain2.edu"
        domain_queries = [f"from:{domain}" for domain in school_domains]
        search_query = " OR ".join(domain_queries)
        
        # Add date filter for recent emails
        date_filter = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
        search_query += f" after:{date_filter}"
        
        print(f"   🔍 Search query: {search_query}")
        
        try:
            # Search for emails
            results = self.service.users().messages().list(
                userId='me',
                q=search_query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print("   📭 No school emails found")
                return []
            
            print(f"   📧 Found {len(messages)} school emails")
            
            # Get full email details
            school_emails = []
            for i, message in enumerate(messages, 1):
                print(f"   📄 Processing email {i}/{len(messages)}...", end='')
                
                email_data = self._get_email_details(message['id'])
                if email_data:
                    school_emails.append(email_data)
                    print(" ✅")
                else:
                    print(" ❌")
            
            print(f"✅ Successfully retrieved {len(school_emails)} school emails")
            return school_emails
            
        except HttpError as error:
            print(f"❌ Error fetching emails: {error}")
            return []
    
    def _get_email_details(self, message_id):
        """
        Get full details of a specific email
        Extracts subject, sender, body, attachments, etc.
        """
        try:
            # Get the email
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id,
                format='full'  # Get full email content
            ).execute()
            
            # Extract email headers
            payload = message['payload']
            headers = payload.get('headers', [])
            
            # Parse headers into dictionary
            header_dict = {header['name'].lower(): header['value'] for header in headers}
            
            # Extract email body
            body = self._extract_email_body(payload)
            
            # Create standardized email data structure
            email_data = {
                'id': message_id,
                'thread_id': message.get('threadId'),
                'timestamp': datetime.fromtimestamp(int(message['internalDate']) / 1000),
                'sender': header_dict.get('from', 'Unknown'),
                'subject': header_dict.get('subject', 'No Subject'),
                'to': header_dict.get('to', ''),
                'body_text': body.get('text', ''),
                'body_html': body.get('html', ''),
                'snippet': message.get('snippet', ''),  # Gmail's auto-preview
                'labels': message.get('labelIds', []),
                'attachments': []  # TODO: Handle attachments in next version
            }
            
            return email_data
            
        except HttpError as error:
            print(f"Error getting email details: {error}")
            return None
    
    def _extract_email_body(self, payload):
        """
        Extract text and HTML body from Gmail message payload
        Gmail API has complex nested structure for email bodies
        """
        body_data = {'text': '', 'html': ''}
        
        # Handle different payload structures
        if 'parts' in payload:
            # Multi-part email (text + HTML + attachments)
            for part in payload['parts']:
                mime_type = part.get('mimeType')
                
                if mime_type == 'text/plain':
                    if 'data' in part['body']:
                        import base64
                        text_data = base64.urlsafe_b64decode(part['body']['data'])
                        body_data['text'] = text_data.decode('utf-8')
                
                elif mime_type == 'text/html':
                    if 'data' in part['body']:
                        import base64
                        html_data = base64.urlsafe_b64decode(part['body']['data'])
                        body_data['html'] = html_data.decode('utf-8')
        else:
            # Simple email (just text or HTML)
            if payload['body'].get('data'):
                import base64
                body_bytes = base64.urlsafe_b64decode(payload['body']['data'])
                body_text = body_bytes.decode('utf-8')
                
                mime_type = payload.get('mimeType')
                if mime_type == 'text/html':
                    body_data['html'] = body_text
                else:
                    body_data['text'] = body_text
        
        return body_data
    
    def send_email(self, to_email, subject, body_html):
        """
        Send email (for urgent alerts and weekly summaries)
        """
        if not self.service:
            print("❌ Gmail service not initialized")
            return False
        
        try:
            import base64
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            print(f"📤 Sending email to {to_email}...")
            
            # Create email
            message = MIMEMultipart('alternative')
            message['to'] = to_email
            message['subject'] = subject
            
            # Add HTML body
            html_part = MIMEText(body_html, 'html')
            message.attach(html_part)
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_message = {'raw': raw_message}
            
            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()
            
            print(f"✅ Email sent successfully (ID: {result['id']})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
            return False

# Educational Tip: Test this module independently
if __name__ == "__main__":
    print("🧪 Testing GmailConnector independently...")
    
    # This requires ConfigManager to work
    import sys
    sys.path.append('.')
    from config_manager import ConfigManager
    
    # Initialize
    config = ConfigManager()
    config.load_schools()
    
    gmail = GmailConnector(config)
    
    # Test authentication
    if gmail.authenticate():
        print("🎉 Gmail authentication working!")
        
        # Test connection
        if gmail.test_connection():
            print("🎉 Gmail connection working!")
            
            # Try to fetch a few recent emails (safe test)
            emails = gmail.get_school_emails(days_back=1, max_results=5)
            print(f"📧 Found {len(emails)} recent school emails")
        else:
            print("❌ Gmail connection test failed")
    else:

        print("❌ Gmail authentication failed")

