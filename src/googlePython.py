'''
Created on 1 Jul 2020

@author: andreas
'''

from __future__ import print_function
import pickle
import os.path

# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib oauth2client
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

CREDENTIALS='google-credentials.json'
TOKENFILE='google-token.pickle'
SCOPES = ['https://www.googleapis.com/auth/documents.readonly',  # If modifying these scopes, delete the file token.pickle
          'https://www.googleapis.com/auth/spreadsheets.readonly',
          'https://www.googleapis.com/auth/drive']
SAMPLE_DOCUMENT_ID = '195j9eDD3ccgjQRttHhJPymLJUCOUjs-jmwTrekvdjFE'
MY_SHEET='1rn_nPJodxAwahIzqfRtEr9HHoqjvmh_7bj6-LUXDRSY'

def quickstart(CREDENTIALS=CREDENTIALS, TOKENFILE=TOKENFILE, SCOPES=SCOPES, 
               SAMPLE_DOCUMENT_ID = SAMPLE_DOCUMENT_ID):
    """
    Example script from the google instructions
    https://developers.google.com/docs/api/quickstart/python
    must run through all those steps, to INITIALIZE api access.
    
    Results in a 'google-token.pickle' file, which can be used as creds.
    """
    print ("Follow the instructions")
    print ("           https://developers.google.com/docs/api/quickstart/python")
    print ("                       Step 1: Turn on the Google Docs API ... etc")
    print ("")
    
    def main():
        """Shows basic usage of the Docs API.
        Prints the title of a sample document.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(TOKENFILE):
            with open(TOKENFILE, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(TOKENFILE, 'wb') as token:
                pickle.dump(creds, token)
    
        service = build('docs', 'v1', credentials=creds)
    
        # Retrieve the documents contents from the Docs service.
        document = service.documents().get(documentId=SAMPLE_DOCUMENT_ID).execute()
    
        print('The title of the document is: {}'.format(document.get('title')))
        
    main()
    
def googleService(servicename='docs', version='v1', TOKENFILE=TOKENFILE):
    if not os.path.exists(TOKENFILE):
        print ("run googlePython.quickstart() to get a tokenfile")
    with open(TOKENFILE, 'rb') as token:
        creds = pickle.load(token)
 
    print("creds: valid=%s, expired=%s, expiry=%s, scopes=%s" % (creds.valid, creds.expired, ("%s"%creds.expiry)[:16], creds.scopes))
    # print("\n".join([m for m in dir(creds) if not m.startswith("_")]))
    
    service = build('docs', 'v1', credentials=creds)
    return service


GOOGLE_STORAGE = 'google-storage.json'
CLIENT_ID_JSON='client_id.json'

def initialize_variant2(GOOGLE_STORAGE = GOOGLE_STORAGE, CLIENT_ID_JSON=CLIENT_ID_JSON):
    """
    might be different might be same
    https://codelabs.developers.google.com/codelabs/gsuite-apis-intro/#7
    """
    from googleapiclient import discovery
    from httplib2 import Http
    from oauth2client import file, client, tools
    
    SCOPES = 'https://www.googleapis.com/auth/drive.readonly.metadata'
    store = file.Storage(GOOGLE_STORAGE)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_ID_JSON, SCOPES)
        creds = tools.run_flow(flow, store)
    DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))
    
    files = DRIVE.files().list().execute().get('files', [])
    for f in files:
        # print(f.keys()); exit()
        print(f['id'], f['kind'], f['name'], f['mimeType'])


def googleAccess(GOOGLE_STORAGE=GOOGLE_STORAGE):
    from oauth2client import file
    store = file.Storage(GOOGLE_STORAGE)
    creds = store.get()
    # print("\n".join([m for m in dir(creds) if not m.startswith("_")]))
    print("creds: invalid=%s, access_token_expired=%s, token_expiry=%s, scopes=%s" % (creds.invalid, creds.access_token_expired, ("%s"%creds.token_expiry)[:16], creds.scopes))
    
    return creds


def showRevisions(creds, fileId=MY_SHEET):
    from googleapiclient import discovery
    from httplib2 import Http
    DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))
    
    revList=DRIVE.revisions().list(fileId = fileId, fields = "*").execute()
    for rev in revList['revisions']:
        url="https://docs.google.com/spreadsheets/export?id=%s&revision=%s&exportFormat=csv&sheet=%s&range=%s" % (fileId, rev['id'], 'ThePast', 'A3:E12')
        print("{id} {kind} {modifiedTime}".format(**rev), url)



if __name__ == '__main__':
    # quickstart()
    # service=googleService()
    
    # or
    
    ## initialize_variant2(CLIENT_ID_JSON='google-credentials.json')
    creds=googleAccess()
    showRevisions(creds=creds)
    