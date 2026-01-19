from __future__ import annotations
import base64, os, mimetypes
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CV_PATH = r'C:\Users\ravik\Downloads\Ravi_Katariya_CV.pdf'

def auth():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as f:
            f.write(creds.to_json())
    return creds

def add_attachment_to_message(service, message_raw, attachment_path):
    # message_raw: base64url string of existing MIME message
    msg_bytes = base64.urlsafe_b64decode(message_raw.encode('utf-8'))
    from email import message_from_bytes
    msg = message_from_bytes(msg_bytes)
    # build multipart with original parts and attachment
    new_msg = MIMEMultipart()
    for k, v in msg.items():
        if k.lower() in ('content-type','mime-version'):
            continue
        new_msg[k] = v
    # attach original payload as plain if exists
    if msg.is_multipart():
        for part in msg.get_payload():
            new_msg.attach(part)
    else:
        from email.mime.text import MIMEText
        new_msg.attach(MIMEText(msg.get_payload(decode=True) or '', _charset='utf-8'))
    ctype, encoding = mimetypes.guess_type(attachment_path)
    maintype, subtype = (ctype or 'application/octet-stream').split('/', 1)
    with open(attachment_path, 'rb') as f:
        part = MIMEBase(maintype, subtype)
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
    new_msg.attach(part)
    return base64.urlsafe_b64encode(new_msg.as_bytes()).decode('utf-8')

def main():
    creds = auth()
    service = build('gmail', 'v1', credentials=creds)
    drafts = service.users().drafts().list(userId='me').execute().get('drafts', [])
    print(f'Found {len(drafts)} drafts')
    for d in drafts:
        did = d['id']
        draft = service.users().drafts().get(userId='me', id=did).execute()
        msg_raw = draft['message']['raw']
        try:
            new_raw = add_attachment_to_message(service, msg_raw, CV_PATH)
            draft_body = {'message': {'raw': new_raw}}
            service.users().drafts().update(userId='me', id=did, body=draft_body).execute()
            print(f'Updated draft {did}')
        except Exception as e:
            print(f'Failed {did}: {e}')

if __name__ == '__main__':
    main()
