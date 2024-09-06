import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from env import scopes
from env import sample_spreadsheet_ID
from env import communities
from fuzzywuzzy import process

def read_google_sheets(name_of_sheet):
    sample_range_name = name_of_sheet + "!A2:B50"
    connected = False
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", scopes
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    while connected == False:
        try:
            service = build("sheets", "v4", credentials=creds)

            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=sample_spreadsheet_ID, range=sample_range_name)
                .execute()
            )
        except HttpError as err:
            connected = False
        else:
            connected = True
    values = result.get("values", None)
    question = []
    answer = []
    if values is None:
        return
    for row in values:
        question.append(row[0])
        answer.append(row[1])
        dictionary = dict(zip(question, answer))
    return dictionary


def understand_question(dictionary, user_question):
    questions = list(dictionary.keys())
    appropriate_question,score = process.extractOne(user_question, questions)
    if score <= 50:
        answer = None
    else:
        answer = dictionary[appropriate_question]
    return answer


def choose_community(user_community):
    community, score = process.extractOne(user_community, communities)
    if score <= 50:
        community = None
    return community
