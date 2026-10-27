
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/calendar.events",
]


def main():
    if not os.path.exists("token.json"):
        print("ERROR: token.json not found.")
        return

    credentials = Credentials.from_authorized_user_file(
        "token.json", SCOPES
    )

    if not credentials.valid:
        print("ERROR: Google authorization is not valid.")
        print("Run google_test.py and authorize again.")
        return

    service = build("tasks", "v1", credentials=credentials)

    lists = service.tasklists().list(maxResults=100).execute()
    task_lists = lists.get("items", [])

    if not task_lists:
        print("No Google Tasks list found.")
        return

    print("Available task lists:")
    for index, task_list in enumerate(task_lists, start=1):
        print(f"{index}. {task_list['title']}")

    try:
        choice = int(input("Choose a list number: "))
        if not 1 <= choice <= len(task_lists):
            print("Invalid list number.")
            return
    except ValueError:
        print("Please enter a number.")
        return

    title = input("Enter your test task: ").strip()

    if not title:
        print("Task title cannot be empty.")
        return

    selected_list = task_lists[choice - 1]

    created_task = service.tasks().insert(
        tasklist=selected_list["id"],
        body={"title": title}
    ).execute()

    print("\nSUCCESS! Task created in Google Tasks.")
    print("Task:", created_task["title"])
    print("List:", selected_list["title"])
    print("Open Google Tasks to verify it.")


if __name__ == "__main__":
    main()