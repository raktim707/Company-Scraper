from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import re
from google.oauth2 import service_account
from bs4 import BeautifulSoup
import requests

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'
credentials=None
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# If modifying these scopes, delete the file token.json.


# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '<Your spreadsheet id>'
SAMPLE_RANGE_NAME = 'Sheet1!K3:K8894'



service = build('sheets', 'v4', credentials=credentials)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range=SAMPLE_RANGE_NAME).execute()
values = result.get('values', [])
reg=re.compile(r'''((\d{3,6})(\s|-|\.)?(\d{3,6})(\s|-|\.)?(\d{3,6})(\s*(ext|x|ext.)\s*(\d{2,5}))?)''')

contact_numbers=[]
count=0
r=requests.Session()
for i in range (len(values)):
    telephone="N/A"
    company_url=values[i][0]
    count=count+1
    if company_url != "N/A":
        try:
            page=r.get(company_url, timeout=2.50)
            print(page.reason)
            soup = BeautifulSoup(page.content, "html.parser")
        except:
            page=None
            print("Broken company url")
        
        if page:
            soup=soup.get_text()
            a=reg.findall(soup)
            print(a)
            if len(a) >= 1:
                if len(a[0]) > 1:
                    telephone=a[0][0]
                else:
                    telephone=a[0]
        print("count:", count, telephone)
    contact_numbers.append([telephone])

print(contact_numbers)
modified = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, valueInputOption="RAW" ,range="Sheet1!N3", body={'values':contact_numbers}).execute()
