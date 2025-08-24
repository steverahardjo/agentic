import sqlparse
from firebase_admin import credentials, firestore
import firebase_admin

from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


class DBConnector:
    def __init__(self, url_path: str, retries: int = 3):
        self.url_path = url_path
        self.retries = retries

    def fetch(self, query: str, table_name: str):
        pass

    def upsert(self, query: str, table: str):
        pass

    def is_value_sql(self, query: str, main_op: str) -> bool:
        parsed = sqlparse.parse(query)
        if not parsed or not parsed[0].tokens:
            return False
        for token in parsed[0].tokens:
            if token.ttype and token.ttype.__name__ == "Keyword":
                return token.value.upper().startswith(main_op)
        return False

class FirebaseConnector:
    def __init__(self, cert_path: str):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cert_path)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def fetch(self, collection: str, filters: dict = None):
        ref = self.db.collection(collection)
        if filters:
            for field, (op, value) in filters.items():
                ref = ref.where(field, op, value)
        docs = ref.stream()
        return [doc.to_dict() for doc in docs]

    def upsert(self, collection: str, data: dict, doc_id: str = None):
        ref = self.db.collection(collection)
        if doc_id:
            ref.document(doc_id).set(data, merge=True)
        else:
            ref.add(data)


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

class GcalendarConnector:
    def __init__(self, token_path :str = None):
        if not token_path:
            flow = InstalledAppFlow.from_client_secrets_file(
            "client_secret.json", SCOPES
        )
            cred = flow.run_local_server(port=8000)
        else:
            cred=Credentials.from_authorized_user_file("token.json", SCOPES)
            
        self.service = build('calendar', "v3", credentials=cred)

    def fetch_calendarPoint(self,start_time:str, end_time:str, max_result:int = 5):
        events_result = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=start_time,
                timeMax=end_time,
                maxResults=max_result,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
        )       
        return events_result
