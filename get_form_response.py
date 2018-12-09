import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
CRED = 'credentials_filename.json'

"""
Set up on the developer console (one time):
1. Create service account
2. Enable Google Sheet API
3. Get credentials for the API with service account
4. Set CRED variable to the path to the credentials file
"""

"""
Set up before running form response parser (every poll):
1. Go to response tab of the form
2. Click the green icon (view response in sheets)
3. Create a Google sheet with name "Escher_Poll_mm_dd_yy" or something like that
4. Share sheet with service account email
"""

credentials = ServiceAccountCredentials.from_json_keyfile_name(CRED, scope)
gc = gspread.authorize(credentials)

# Sample form response sheet name
FORM_NAME = "Escher_Poll_{}/{}/{}".format('12', '08', '18')

wks = gc.open(FORM_NAME).sheet1
# wks is much like panda, can then do data manipulation and stuff
