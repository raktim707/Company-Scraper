from bs4 import BeautifulSoup
import requests
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from utils import find_nature, name_of_psc

from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'
credentials=None
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# If modifying these scopes, delete the file token.json.


# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1t3ofZBBq7oxs5rPRHjKEN8gQvkfnJ8v4iyEXQsjaOCA'
SAMPLE_RANGE_NAME = ["Sheet1!C705:D780", "Sheet1!Q705:R780"]



service = build('sheets', 'v4', credentials=credentials)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().batchGet(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            ranges=SAMPLE_RANGE_NAME).execute()
values = result.get('valueRanges', [])

branches=values[0].get("values",[])
company_urls= values[1].get('values',[])

r=requests.Session()
count=0
base_url="https://find-and-update.company-information.service.gov.uk"
s_to_ac=[]
for i, url in zip(branches, company_urls):
        count=count+1
        company_name=None
        company_number=None
        office=None
        psc1=None
        psc2=None
        psc3=None
        psc4=None
        psc1_nature = None
        psc2_nature=None
        psc3_nature=None
        psc4_nature = None
        valid=False
        try:
                branch=int(i[1])
                valid=True
        except IndexError:
                valid=False
                print("No branch detected")
        
        if valid:
                if branch < 5:
                        try:
                                web_url = url[1]
                                print(web_url)
                                page = r.get(web_url, timeout=2.50, headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.5', 'Connection': 'keep-alive', 'Host': 'www.zoopla.co.uk'})
                                print("doc url: ", page.reason, page.status_code)
                                soup = BeautifulSoup(page.content, "html.parser")
                        except:
                                page=None
                        
                        if page and page.status_code==200:
                                tags=soup.select("li.type-company:nth-child(1) > h3:nth-child(1) > a:nth-child(1)")
                                if tags:
                                        slug=tags[0].get('href')
                                        company_name = tags[0].get_text(strip=True)
                                        company_number=slug.split('/')[-1]
                                        office_tag=soup.select("li.type-company:nth-child(1) > p:nth-child(3)")
                                        if office_tag:
                                                office=office_tag[0].get_text(strip=True)
                                        
                                        detail_url = base_url+slug+'/persons-with-significant-control'
                                        
                                        try:
                                                company_page=r.get(detail_url, timeout=2.50, headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.5', 'Connection': 'keep-alive', 'Host': 'www.zoopla.co.uk'})
                                                print(company_page.reason)
                                                soupCompany=BeautifulSoup(company_page.content, "html.parser")
                                        except:
                                                print("Company detail link error")
                                                company_page=None
                                        
                                        if (company_page is not None and company_page.status_code==200) and company_number is not None:
                                                psc1_name=soupCompany.find("div", class_="appointment-1")
                                                psc2_name=soupCompany.find("div", class_="appointment-2")
                                                psc3_name=soupCompany.find("div", class_="appointment-3")
                                                psc4_name=soupCompany.find("div", class_="appointment-4")
                                                
                                                if psc1_name is not None:
                                                        psc1=name_of_psc(psc1_name)
                                                        psc1_nature=find_nature(psc1_name)
                                                
                                                if psc2_name is not None:
                                                        psc2=name_of_psc(psc2_name)
                                                        psc2_nature=find_nature(psc2_name)
                                                
                                                if psc3_name is not None:
                                                        psc3=name_of_psc(psc3_name)
                                                        psc3_nature=find_nature(psc3_name)
                                                
                                                if psc4_name is not None:
                                                        psc4=name_of_psc(psc4_name)
                                                        psc4_nature=find_nature(psc4_name)
                                                print(count, company_name, company_number, office)
                                                print(psc1, psc1_nature, psc2, psc2_nature, psc3, psc3_nature, psc4, psc4_nature)
        s_to_ac.append([company_name, company_number, office, psc1, psc1_nature, psc2, psc2_nature, psc3, psc3_nature, psc4, psc4_nature])

modified = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, valueInputOption="RAW" ,range="Sheet1!S705", body={'values':s_to_ac}).execute()
print(s_to_ac)             
        
