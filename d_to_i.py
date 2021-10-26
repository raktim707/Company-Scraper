from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

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
SAMPLE_SPREADSHEET_ID = '<Your spreadsgeet id>'
SAMPLE_RANGE_NAME = 'Sheet1!A3:C'



service = build('sheets', 'v4', credentials=credentials)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range=SAMPLE_RANGE_NAME).execute()
values = result.get('values', [])
print(len(values))
d_to_i=[]
count=0
r=requests.Session()
for i in range(len(values)):
        count=count+1
        try:
                web_url = values[i][1]
        except IndexError:
                web_url=None
        print(web_url)
        sale=0
        rent=0
        logo = None
        contact=None
        city=None
        post_code=None
        branch= None
        try:
                page = r.get(web_url, timeout=2.50)
                print(page.reason)
                soup = BeautifulSoup(page.content, "html.parser")
                branch = soup.find("span", class_="listing-results-utils-count")
        except:
                page=None
                print("Something went wrong")

        if page and page.status_code ==200:
                
                if branch is not None:
                        branch= branch.get_text(strip=True)
                        branch=branch.split()[-1]

                        if int(branch) <=5:
                                tags=soup.find_all("div", class_="agents-stats-l")
                                rent=0
                                sale=0
                                for tag in tags:
                                        s=tag.get_text(strip=True)
                                        s=s.split(":")
                                        res=s[0].split()
                                        if len(res)==3 and res[0]=="Residential":
                                                if res[2]=='sale':
                                                        sale=sale+int(s[1])
                                                elif res[2]=='rent':
                                                        rent=rent+int(s[1])
                                        print(sale, rent)

                                address=soup.select(".agents-results-copy > p:nth-child(1) > span:nth-child(1)")
                                
                                if address is not None:
                                        for detail in address:
                                                contact_details=detail.get_text(strip=True)
                                                if ('We also' in contact_details or 'we also' in contact_details) and '-' in contact_details:
                                                        print('before: ',contact_details)
                                                        contact_details=contact_details.split(' -')[:-1]
                                                        print("after split: ", contact_details)
                                                        contact_details=''.join(contact_details).strip()
                                                        contact_details = contact_details.split(',')
                                                        print("contact details: ", contact_details)
                                                else:
                                                        contact_details=contact_details.split(',')
                                                if len(contact_details)==2:
                                                        contact=contact_details[-2].strip()
                                                        city=None                                                        
                                                else:
                                                        contact=''.join(contact_details[:-2]).strip()
                                                        city=contact_details[-2].strip()
                                                post_code = (contact_details[-1]).strip()
                                                print("Count: ", count, contact, city, post_code)

                                image=soup.select(".lazy")
                                for tag in image:
                                        logo=tag['data-src']
        d_to_i.append([branch, rent, sale, contact, city, post_code, logo])


modified = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, valueInputOption="RAW" ,range="Sheet1!D3", body={'values':d_to_i}).execute()
