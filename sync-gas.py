from __future__ import print_function

import os.path
import json
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/script.projects.readonly']

ext = {
    'SERVER_JS': 'js',
    'JSON': 'json',
    'HTML': 'html'
}

DEST_FOLDER = None


def extract_sources(files):
    for f in files:
        fn = f['name']
        ftype = f['type']  # SERVER_JS, JSON, HTML
        fsource = f['source']
        fn += "." + (ext[ftype] if ftype in ext else ftype)
        print(f"Exporting file {fn}...")
        with open(os.path.join(DEST_FOLDER, fn), encoding="utf-8", mode="w") as f:
            f.write(fsource)


def main():
    """Shows basic usage of the Apps Scripts API.
    Prints values from a sample spreadsheet.
    """

    global DEST_FOLDER
    SCRIPT_ID = sys.argv[1]
    DEST_FOLDER = sys.argv[2]

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('script', 'v1', credentials=creds)

        # Call the Script API
        request = service.projects().getContent(scriptId=SCRIPT_ID)
        response = request.execute()
        extract_sources(response['files'])
        print("That's all, folks!")
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    print("usage: sync-gas <script_id> <dest_folder>")
    main()
