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


def save_sources(files, dest_folder):
    for f in files:
        fn = f['name']
        ftype = f['type']  # SERVER_JS, JSON, HTML
        fsource = f['source']
        fn += "." + (ext[ftype] if ftype in ext else ftype)
        print(f"Exporting file {fn}...")
        with open(os.path.join(dest_folder, fn), encoding="utf-8", mode="w") as f:
            f.write(fsource)


def main():
    """Shows basic usage of the Apps Scripts API.
    Prints values from a sample spreadsheet.
    """

    COMMAND = sys.argv[1]
    if COMMAND not in ['download', 'upload']:
        raise Exception('Wrong command argument, should be one of "download" or "upload"')
    SCRIPT_ID = sys.argv[2]
    DEST_FOLDER = sys.argv[3]
    

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

        if COMMAND == 'download':
            request = service.projects().getContent(scriptId=SCRIPT_ID)
            response = request.execute()
            save_sources(response['files'], DEST_FOLDER)
        if COMMAND == 'upload':
            raise Exception('Upload command hasn\'t implemented yet')
        print("That's all, folks!")
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    print("usage: sync-gas <download/upload> <script_id> <dest_folder>")
    main()
