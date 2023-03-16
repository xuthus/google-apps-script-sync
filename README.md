# sync-apps-script-project

Syncs Google Apps Script project with local sources folder

usage:
```bash
sync-gas.py <download/upload> <script_id> <local_folder>
```

Requires `credentials.json` to authenticate with Google Script project.
> To get it visit Google Cloud Console and create OAuth credentials (read more here - https://developers.google.com/workspace/guides/create-credentials).

Creates `token.json` file to store authentication token. 
