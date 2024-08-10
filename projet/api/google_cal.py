import base64
import datetime
import os.path
import time
from urllib.parse import urlencode
from uuid import uuid4
from zoneinfo import ZoneInfo
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from icalendar import Calendar, Event

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
    if creds is None or not creds.valid:
        try:
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
        except Exception as e:
            print(e)
            print("Veuillez ajouter le fichier Credentials.json disponible avec votre projet Google ou une autre erreur est survenue")
            return None
    else:
        return creds

def add_event_reservation(title:str,attendee_phone:str,attendee_name:str,attendee_surname:str,description:str,date_start:datetime.datetime,date_end:datetime.datetime)->str:
    creds = login()
    date_start_iso = date_start.astimezone(ZoneInfo('Europe/Paris')).isoformat()
    date_end_iso = date_end.astimezone(ZoneInfo('Europe/Paris')).isoformat()
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



# https://learnpython.com/blog/working-with-icalendar-with-python/
def create_ical_event(title:str,attendee_phone:str,attendee_name:str,attendee_surname:str,description:str,date_start:datetime.datetime,date_end:datetime.datetime)->str:
    cal = Calendar()
    cal.add('prodid','WiREV calendar')
    cal.add('version','2.0')
    event = Event()
    event.add('summary',title)
    event.add('description',f"{description}\n{attendee_surname} {attendee_name}\nNuméro: {attendee_phone}")
    event.add('dtstart',date_start.astimezone(ZoneInfo('Europe/Paris')))
    event.add('dtend',date_end.astimezone(ZoneInfo('Europe/Paris')))
    cal.add_component(event)
    try:
        uuid_file = str(uuid4())
        if not os.path.exists('./tmp'):
            os.mkdir('./tmp',511)
        with open(f'./tmp/{uuid_file}.ics',"wb") as f:
            f.write(cal.to_ical())
        
        return uuid_file
    except Exception as e:
        print(e)
        return ""
def delete_ics_older_than_duration(duration_secs:int):
    try:
        if os.path.exists('./tmp'):
            print(os.listdir('./tmp/'))
            for f in os.listdir('./tmp/'):
                f = os.path.join('./tmp',f)
                if os.stat(f).st_mtime < (time.time() - duration_secs):
                    os.remove(f)
                    print(f'Deleted {f}')
        else:
            print("Wrong path")
    except Exception as e:
        print(f"An error occured while deleting old ics files: {e}")

# Added http://localhost:4545/ as authorized return uri in https://console.cloud.google.com/apis/credentials
# https://developers.google.com/calendar/api/guides/create-events#python


if __name__ == "__main__":
    creds = login()
    if creds is not None:
        print("Vous êtes bien connecté ou l'êtes à présent.")
    else:
        print("Une erreur est survenue lors de la génération de Token.")
