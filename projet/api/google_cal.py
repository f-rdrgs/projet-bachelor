import datetime
import os.path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

# https://developers.google.com/calendar/api/quickstart/python
def login():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            flow.redirect_uri= "http://localhost:4545"
            creds = flow.run_local_server(port=4545)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def add_event_reservation(title:str,attendee_phone:str,attendee_name:str,attendee_surname:str,description:str,date_start:datetime.datetime,date_end:datetime.datetime)->str:
    creds = login()
    date_start_iso = date_start.astimezone().isoformat()
    date_end_iso = date_end.astimezone().isoformat()
    try:
        service = build("calendar", "v3", credentials=creds)
        print(f"Start {date_start} End {str(date_end)}")
        event = {
            "summary": title,
            "description":f"{description}\n{attendee_surname} {attendee_name}\nNuméro: {attendee_phone}",
            "start":{
                "dateTime":str(date_start_iso),
                "timeZone":"Europe/Paris"
            },
            "end":{
                "dateTime":str(date_end_iso),
                "timeZone":"Europe/Paris"
            }
        }

        event = service.events().insert(calendarId='primary',body=event).execute()
        detail = f"{description}\n{attendee_surname} {attendee_name}\nNuméro: {attendee_phone}"
        link_cal = gen_share_link_google_cal(title,date_start_iso,date_end_iso,detail)
        print(f"Created event at link: {link_cal}")
        return link_cal
    except Exception as e:
        print(f"An error occured when adding event: {e}")

def gen_share_link_google_cal(summary:str,date_start:datetime.datetime,date_end:datetime.datetime,details:str)->str:
    event = {
        'action': 'TEMPLATE',
        'text': summary,
        'dates': f"{str(date_start).replace(':', '').replace('-', '')}/{str(date_end).replace(':', '').replace('-', '')}",
        'details': details
    }
    base_url = "https://calendar.google.com/calendar/r/eventedit"
    return f"{base_url}?{urlencode(event)}"


# Added http://localhost:4545/ as authorized return uri in https://console.cloud.google.com/apis/credentials
# https://developers.google.com/calendar/api/guides/create-events#python
# if __name__ == "__main__":
#   add_event_reservation("Réservation Terrain de tennis","995830193","Smith","Michael","Une réservation de terrain de tennis",datetime.datetime(2024,6,26,14,30,0,tzinfo=ZoneInfo('Europe/Paris')),datetime.datetime(2024,6,26,15,0,0,tzinfo=ZoneInfo('Europe/Paris')))

if __name__ == "__main__":
    date_og = datetime.datetime.fromisoformat("2024-06-25T14:35:25.143736")
    new_date = datetime.datetime(date_og.year,date_og.month,date_og.day,14,50,0,tzinfo=ZoneInfo("Europe/Paris"))
    print(new_date)
    print(gen_share_link_google_cal("AAAAA","2025-07-05 16:30:00","2025-07-05 17:00:00","HAHHAHAH"))