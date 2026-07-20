from abc import ABC, abstractmethod

class BaseCommunicationProvider(ABC):
    @abstractmethod
    def authenticate(self):
        """Authenticate with the external provider."""
        pass

    @abstractmethod
    def get_account_profile(self):
        """Fetch the account profile details (e.g. email address, historyId)."""
        pass

    @abstractmethod
    def fetch_message_ids(self, sync_cursor: str = None, query: str = None):
        """Fetch a list of message IDs for sync."""
        pass

    @abstractmethod
    def fetch_message_detail(self, provider_message_id: str):
        """Fetch the full detail of a specific message."""
        pass

    @abstractmethod
    def fetch_attachment(self, provider_message_id: str, provider_attachment_id: str):
        """Fetch a specific attachment from a message."""
        pass
