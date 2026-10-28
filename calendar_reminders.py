
import os
import threading
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TIME_ZONE = "Asia/Colombo"

SCOPES = [
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/calendar.events",
]

CHECK_INTERVAL = 15
REMINDER_GRACE_SECONDS = 90


def get_calendar_service():
    """Connect to Google Calendar using the existing token."""

    if not os.path.exists("token.json"):
        raise FileNotFoundError(
            "token.json was not found in the project folder."
        )

    credentials = Credentials.from_authorized_user_file(
        "token.json", SCOPES
    )

    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            raise RuntimeError(
                "Google authorization is invalid. "
                "Run google_test.py and authorize again."
            )

    return build("calendar", "v3", credentials=credentials)


def monitor_calendar(speak_callback, stop_event):
    """Check Google Calendar and announce reminders when due."""

    announced_ids = set()
    service = None

    while not stop_event.is_set():
        try:
            if service is None:
                service = get_calendar_service()

            now = datetime.now(ZoneInfo(TIME_ZONE))
            window_start = now - timedelta(
                seconds=REMINDER_GRACE_SECONDS
            )

            events_result = service.events().list(
                calendarId="primary",
                timeMin=window_start.isoformat(),
                timeMax=(now + timedelta(seconds=1)).isoformat(),
                singleEvents=True,
                orderBy="startTime",
                maxResults=50,
            ).execute()

            events = events_result.get("items", [])

            for event in events:
                event_id = event.get("id")

                if not event_id or event_id in announced_ids:
                    continue

                if event.get("status") == "cancelled":
                    continue

                start = event.get("start", {})
                start_text = start.get("dateTime")

                # Skip all-day events.
                if not start_text:
                    continue

                start_time = datetime.fromisoformat(start_text)

                if start_time.tzinfo is None:
                    start_time = start_time.replace(
                        tzinfo=ZoneInfo(TIME_ZONE)
                    )

                seconds_late = (now - start_time).total_seconds()

                if 0 <= seconds_late <= REMINDER_GRACE_SECONDS:
                    title = event.get("summary", "Untitled reminder")
                    announced_ids.add(event_id)

                    speak_callback(
                        f"Reminder. {title}."
                    )

        except HttpError as error:
            print(f"Calendar API error: {error}")
            service = None

        except Exception as error:
            print(f"Reminder monitor error: {error}")
            service = None

        stop_event.wait(CHECK_INTERVAL)


def start_reminder_monitor(speak_callback):
    """Start the calendar monitor in a background thread."""

    stop_event = threading.Event()

    worker = threading.Thread(
        target=monitor_calendar,
        args=(speak_callback, stop_event),
        daemon=True,
    )

    worker.start()
    print("JARVIS Calendar reminder monitor started.")

    return stop_event
