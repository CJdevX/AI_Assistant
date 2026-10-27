import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/calendar.events",
]


def main():
    credentials = None

    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file(
            "token.json", SCOPES
        )

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            credentials = flow.run_local_server(port=0)

        with open("token.json", "w", encoding="utf-8") as token_file:
            token_file.write(credentials.to_json())

    try:
        service = build("tasks", "v1", credentials=credentials)
        result = service.tasklists().list(maxResults=10).execute()
        task_lists = result.get("items", [])

        print("\nSUCCESS! Google Tasks connected.")

        if task_lists:
            print("\nYour Google Tasks lists:")
            for task_list in task_lists:
                print("-", task_list["title"])
        else:
            print("\nNo task lists found.")

        # calendar = build("calendar", "v3", credentials=credentials)
        # calendar.calendarList().list(maxResults=1).execute()

        calendar = build("calendar", "v3", credentials=credentials)

        calendar.events().list(
            calendarId="primary",
            maxResults=1
        ).execute()

        
        print("\nSUCCESS! Google Calendar connected.")

    except HttpError as error:
        print("\nGoogle API error:", error)
    except Exception as error:
        print("\nConnection error:", error)


if __name__ == "__main__":
    main()