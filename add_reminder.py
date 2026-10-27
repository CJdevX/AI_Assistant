
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TIME_ZONE = "Asia/Colombo"

SCOPES = [
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/calendar.events",
]


def main():
    if not os.path.exists("token.json"):
        print("ERROR: token.json not found. Run google_test.py first.")
        return

    credentials = Credentials.from_authorized_user_file(
        "token.json", SCOPES
    )

    if not credentials.valid:
        print("ERROR: Google authorization is not valid.")
        print("Run google_test.py and authorize again.")
        return

    title = input("Reminder title: ").strip()
    if not title:
        print("Title cannot be empty.")
        return

    print("\nEnter the reminder date and time.")
    print("Date format: YYYY-MM-DD (example: 2026-10-30)")
    print("Time format: HH:MM in 24-hour format (example: 20:00)")

    date_text = input("Date: ").strip()
    time_text = input("Time: ").strip()

    try:
        reminder_time = datetime.strptime(
            f"{date_text} {time_text}", "%Y-%m-%d %H:%M"
        ).replace(tzinfo=ZoneInfo(TIME_ZONE))
    except ValueError:
        print("Invalid date or time format.")
        return

    now = datetime.now(ZoneInfo(TIME_ZONE))

    if reminder_time <= now:
        print("Please enter a future date and time.")
        return

    end_time = reminder_time + timedelta(minutes=5)

    event = {
        "summary": f"JARVIS Reminder: {title}",
        "description": "Reminder created by JARVIS.",
        "start": {
            "dateTime": reminder_time.isoformat(),
            "timeZone": TIME_ZONE,
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": TIME_ZONE,
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 0},
                {"method": "email", "minutes": 0},
            ],
        },
    }

    try:
        calendar = build("calendar", "v3", credentials=credentials)

        created_event = calendar.events().insert(
            calendarId="primary",
            body=event,
        ).execute()

        print("\nSUCCESS! Calendar reminder created.")
        print("Title:", title)
        print("Date and time:", reminder_time.strftime("%Y-%m-%d %H:%M"))
        print("Time zone:", TIME_ZONE)
        print("Open event:", created_event.get("htmlLink"))

        print(
            "\nCheck your Google Calendar notification settings "
            "and device permissions."
        )

    except HttpError as error:
        print("\nGoogle Calendar API error:", error)


if __name__ == "__main__":
    main()