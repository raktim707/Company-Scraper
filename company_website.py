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
SAMPLE_SPREADSHEET_ID = '<Your spreadsheet id>'
SAMPLE_RANGE_NAME = 'Sheet1!B3:D'



service = build('sheets', 'v4', credentials=credentials)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range=SAMPLE_RANGE_NAME).execute()
values = result.get('values', [])
print(len(values))

count=0
slug = None
company_web=[]
branch=6
base_url="https://www.zoopla.co.uk"
r=requests.Session()
for i in range(len(values)):
    company_website="N/A"
    count=count+1
    try:
            branch=int(values[i][2])
            web_url = values[i][0]
    except IndexError:
            web_url=None
    if branch < 5 and web_url:
        try:
                page = r.get(web_url, timeout=2.50)
                print(page.reason)
                soup = BeautifulSoup(page.content, "html.parser")
                company_slug = soup.select(".agents-results-item > h2:nth-child(2) > a:nth-child(1)")
                if company_slug:
                    slug=company_slug[0].get("href")
        except:
                page=None
                print("Something went wrong")

        if slug:
            company_detail_url=base_url + slug
            print(company_detail_url)
            try:
                company_detail_page = r.get(company_detail_url, timeout=2.50)
                print(company_detail_page.reason)
                soup = BeautifulSoup(company_detail_page.content, "html.parser")
            except:
                company_detail_page=None
                print("Company detail page link broken")
        
            if company_detail_page:
                company_tag=soup.select("div.sidebar:nth-child(5) > h5:nth-child(1) > a:nth-child(1)")
                if company_tag:
                    company_website=company_tag[0].get("href")
                    print(count, " Company_website: ", company_website)
    company_web.append([company_website])

print(count, company_web)
modified = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, valueInputOption="RAW" ,range="Sheet1!K3", body={'values':company_web}).execute()



            
