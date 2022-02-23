from google_auth_oauthlib.flow import InstalledAppFlow

if __name__ == "__main__":
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    flow = InstalledAppFlow.from_client_secrets_file('configs/credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    with open('tokens/mainToken.json', 'w') as token:
        token.write(creds.to_json())
