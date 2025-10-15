
import sqlparse
from datetime import datetime
from typing import Any, Dict, List, Optional

# Local abstract interface
from agentic.tools.mcp_connector import BaseConnector

try:
    from firebase_admin import credentials, firestore
    import firebase_admin
except Exception:
    # Allow import-time failure for environments without firebase installed
    firebase_admin = None

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
except Exception:
    Credentials = None
    build = None
    InstalledAppFlow = None


class FirebaseConnector(BaseConnector):
    def __init__(self, cert_path: Optional[str] = None):
        if firebase_admin is None:
            raise RuntimeError("firebase_admin is not available in this environment")
        if not firebase_admin._apps:
            if not cert_path:
                raise ValueError("cert_path is required to initialize Firebase app")
            cred = credentials.Certificate(cert_path)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    # In addition to generic fetch/upsert, provide get_user/save_user expected by Tooling
    def get_user(self, document_id: str) -> Optional[Dict[str, Any]]:
        doc_ref = self.db.collection("users").document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    def save_user(self, document_id: str, data: Dict[str, Any]) -> bool:
        try:
            self.db.collection("users").document(document_id).set(data, merge=True)
            return True
        except Exception:
            return False

    def fetch(self, collection: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        ref = self.db.collection(collection)
        if filters:
            for field, (op, value) in filters.items():
                ref = ref.where(field, op, value)
        docs = ref.stream()
        return [doc.to_dict() for doc in docs]

    def upsert(self, collection: str, data: Dict[str, Any], doc_id: Optional[str] = None) -> Optional[str]:
        ref = self.db.collection(collection)
        if doc_id:
            ref.document(doc_id).set(data, merge=True)
            return doc_id
        else:
            new_doc = ref.add(data)
            try:
                return new_doc[0].id
            except Exception:
                return None


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class GcalendarConnector:
    def __init__(self, token_path: Optional[str] = None):
        if InstalledAppFlow is None or build is None:
            raise RuntimeError("google api libraries are not available in this environment")

        if not token_path:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            cred = flow.run_local_server(port=8000)
        else:
            cred = Credentials.from_authorized_user_file(token_path, SCOPES)

        self.service = build("calendar", "v3", credentials=cred)

    def fetch_calendarPoint(self, start_time: str, end_time: str, max_result: int = 5) -> Dict[str, Any]:
        events_result = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=start_time,
                timeMax=end_time,
                maxResults=max_result,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result
    
    def push_

class PostGresConnector:
    def __init__(self):
        pass


