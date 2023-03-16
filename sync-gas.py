from __future__ import print_function

import os.path
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/script.projects']

extensions = {
    'SERVER_JS': 'js',
    'JSON': 'json',
    'HTML': 'html'
}


def save_sources(files, local_folder: str):
    for file_info in files:
        #print(file_info)
        filename = file_info['name'] + "." + (
            extensions[file_info['type']] if file_info['type'] in extensions else file_info['type'])
        print(f"Exporting file {filename}...")
        with open(os.path.join(local_folder, filename), encoding="utf-8", mode="w") as fw:
            fw.write(file_info['source'])


def get_file_type(filename: str) -> str:
    if filename.lower().endswith('.js'):
        return 'SERVER_JS'
    if filename.lower().endswith('.json'):
        return 'JSON'
    if filename.lower().endswith('.html'):
        return 'HTML'
    raise Exception(f'Unrecognized file type: {filename}')


def upload_sources(service: str, script_id: str, local_folder: str):
    request = {
        'files': []
    }
    for filename in os.listdir(local_folder):
        with open(os.path.join(local_folder, filename), mode='r', encoding="utf-8") as f:
            request['files'].append({
                'name': os.path.splitext(filename)[0],
                'type': get_file_type(filename),
                'source': f.read()
            })
    response = service.projects().updateContent(
        body=request,
        scriptId=script_id).execute()
    print(response)


def main():
    if len(sys.argv) != 4:
        raise Exception('Not enough command line arguments, should be 3')
    cmd: str = sys.argv[1]
    if cmd not in ['download', 'upload']:
        raise Exception('Wrong command argument, should be one of "download" or "upload"')
    script_id: str = sys.argv[2]
    local_folder: str = sys.argv[3]

    try:
        service = build('script', 'v1', credentials=get_credentials())

        if cmd == 'download':
            request = service.projects().getContent(scriptId=script_id)
            response = request.execute()
            save_sources(response['files'], local_folder)

        if cmd == 'upload':
            upload_sources(service, script_id, local_folder)

        print("That's all, folks!")
    except HttpError as err:
        print(err)


def get_credentials() -> Credentials:
    credentials = None
    if os.path.exists('token.json'):
        credentials = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            credentials = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())
    return credentials


if __name__ == '__main__':
    print("usage: sync-gas.py <download/upload> <script_id> <local_folder>")
    main()
