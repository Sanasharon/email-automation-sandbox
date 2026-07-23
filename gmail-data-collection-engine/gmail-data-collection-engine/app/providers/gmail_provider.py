from app.providers.base_provider import BaseCommunicationProvider
from app.auth.gmail_oauth import get_gmail_credentials, create_gmail_service, get_authenticated_gmail_profile

class GmailProvider(BaseCommunicationProvider):
    def __init__(self):
        self.creds = None
        self.service = None

    def authenticate(self, interactive: bool = True):
        """Authenticates via Desktop OAuth and initializes the Gmail service."""
        self.creds = get_gmail_credentials(interactive=interactive)
        self.service = create_gmail_service(self.creds)

    def get_account_profile(self):
        """Returns the profile containing emailAddress and historyId."""
        if not self.service:
            raise Exception("Provider not authenticated. Call authenticate() first.")
        return get_authenticated_gmail_profile(self.service)

    def fetch_message_ids(self, sync_cursor: str = None, query: str = None, max_results: int = None):
        """Yields message IDs, handling pagination internally."""
        if not self.service:
            raise Exception("Provider not authenticated. Call authenticate() first.")
        
        req = self.service.users().messages().list(
            userId='me', 
            maxResults=100 if not max_results else min(100, max_results), 
            q=query
        )
        yielded_count = 0
        
        while req is not None:
            res = req.execute()
            messages = res.get('messages', [])
            for msg in messages:
                if max_results and yielded_count >= max_results:
                    return
                yield msg['id']
                yielded_count += 1
            req = self.service.users().messages().list_next(req, res)

    def fetch_incremental_message_ids(self, start_history_id: str):
        """
        Uses history.list to fetch incrementally.
        Returns: (deduplicated_message_ids_list, final_history_id_str, pages_processed_int)
        Raises HttpError if history is expired (404).
        """
        if not self.service:
            raise Exception("Provider not authenticated. Call authenticate() first.")
            
        message_ids = set()
        pages_processed = 0
        latest_history_id = start_history_id
        
        req = self.service.users().history().list(
            userId='me',
            startHistoryId=start_history_id
        )
        
        while req is not None:
            res = req.execute()
            pages_processed += 1
            
            # Update latest_history_id if present in this page
            if 'historyId' in res:
                latest_history_id = str(res['historyId'])
                
            history_records = res.get('history', [])
            for record in history_records:
                # 1. Check messagesAdded
                for msg_added in record.get('messagesAdded', []):
                    msg_id = msg_added.get('message', {}).get('id')
                    if msg_id:
                        message_ids.add(msg_id)
                # 2. Check direct messages in record
                for msg in record.get('messages', []):
                    msg_id = msg.get('id')
                    if msg_id:
                        message_ids.add(msg_id)
                # 3. Check labelsAdded (e.g. INBOX label added)
                for lbl_added in record.get('labelsAdded', []):
                    msg_id = lbl_added.get('message', {}).get('id')
                    if msg_id:
                        message_ids.add(msg_id)
                # 4. Check labelsRemoved (e.g. DRAFT or UNREAD label removed)
                for lbl_rem in record.get('labelsRemoved', []):
                    msg_id = lbl_rem.get('message', {}).get('id')
                    if msg_id:
                        message_ids.add(msg_id)
                        
            req = self.service.users().history().list_next(req, res)
            
        return list(message_ids), latest_history_id, pages_processed

    def fetch_message_detail(self, provider_message_id: str):
        """Fetches the full detail of a specific message."""
        if not self.service:
            raise Exception("Provider not authenticated. Call authenticate() first.")
        return self.service.users().messages().get(
            userId='me', 
            id=provider_message_id, 
            format='full'
        ).execute()

    def fetch_attachment(self, provider_message_id: str, provider_attachment_id: str):
        """Fetches base64url encoded attachment payload from Gmail."""
        if not self.service:
            raise Exception("Provider not authenticated. Call authenticate() first.")
        return self.service.users().messages().attachments().get(
            userId='me',
            messageId=provider_message_id,
            id=provider_attachment_id
        ).execute()
