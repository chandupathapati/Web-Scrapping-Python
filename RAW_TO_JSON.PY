import requests
from bs4 import BeautifulSoup
import urllib3
import pandas as pd
import json
import re
import pandas



# define the source url
source_url = 'http://www.dot.ca.gov'

#get the html data from source url
page = requests.get(source_url+"/mail.htm")

#prase the data
soup = BeautifulSoup(page.text, 'html.parser')

#define html keys
json_tags = ['office_name', 'office_link', 'office_address', 'office_city',
'office_state', 'office_zip', 'office_phone', 'mail_address',
'mail_pobox', 'mail_city', 'mail_state', 'mail_zip', 'mail_phone']

#To initialize json schema
def initialize_json_row():
    json_row = dict([(tag,None) for tag in json_tags])
    return json_row


#Convert raw data to json
def get_json_from_row(row):

    #filter td tags from the parsed row
    cols = row.find_all('td')

    #to exclude the last row of the table which contains irrevelent data
    if(len(cols)==2):
        column_1 = cols[0] #pysical office address
        column_2 = cols[1] #Mailing address
        json_data = initialize_json_row()
        #filter all a tags
        hyperlink = column_1.find_all("a")[0]

        #extract hyper lins from a tags
        json_data["office_link"] = source_url + hyperlink.get('href')

        #split by new line charecter and get the office address information
        office_info = [info.strip() for info in column_1.text.split("\n")]

        #removing duplicate new line charecters data
        if(len(office_info)>4):
                 office_info[0]=office_info[0]+" "+office_info[1]
                 office_info.pop(1)

        #office name from office info record
        json_data["office_name"] = office_info[0]

        #office address from info record and strip the extra spaces
        json_data["office_address"] = office_info[1].replace(u'\xa0', u' ').strip()

        #office city from office info record and split by ',' and get the recod in 0 index
        json_data["office_city"] = office_info[2].split(",")[0]

        #office state from office info record by spliting and removing extra spaces
        json_data["office_state"] = office_info[2].split(",")[1].strip().split(" ")[0] if "," in office_info[2] and " "in office_info[2].split(",")[1] else None

        #office zip from office info record by spliting and removing extra spaces
        json_data["office_zip"] = office_info[2].split(",")[1].strip().split(" ")[1] if "," in office_info[2] and " "in office_info[2].split(",")[1] else None

        #office phone from office info record
        json_data["office_phone"] = office_info[3].strip()

        #remove special charecters in mailing address data
        mailing_info = [info.replace(u'\xa0', u' ').strip() for info in column_2.text.split("\r\n")]

        #get the mailing address data from mailing info and check if it is a po address or mailing address
        json_data["mail_address"] = mailing_info[0] if (len(re.findall('[p|P].+[o|O.]',mailing_info[0]))==0) else None

        #check for the existanence of P O box informations
        po_box_list = [po_box for po_box in mailing_info if len(re.findall('[p|P].+[o|O.]',po_box))>0]

        #data for po box if exists
        json_data["mail_pobox"] = po_box_list[0] if len(po_box_list)>0 else None

        #get mail city from mailing info
        json_data["mail_city"] = [ city.split(",")[0] for city in mailing_info if "," in city][0]

        #get the mail state by spliting and striping mailing info record
        json_data["mail_state"] = [ city.split(",")[1].strip().split(" ")[0] for city in mailing_info if "," in city][0]

        #
        json_data["mail_zip"] = [ city.split(",")[1].strip().split(" ",1)[1].strip() for city in mailing_info if "," in city][0]

        #pattern to find the phone number
        pattern = "[0-9]+[-][0-9]+[-][0-9]+"

        #if pattern matches the assign the phone number
        json_data["mail_phone"] = mailing_info[-1] if re.match(pattern, mailing_info[-1]) is not None else None

        return json_data

#method to fetch data and retun json data
def Caltrans_office_JSON_Data():
    rows = soup.find_all('tr')
    data = list(filter(lambda row: row is not None ,[get_json_from_row(row) for row in rows]))
    return data

#print json data
print(json.dumps(Caltrans_office_JSON_Data(), indent=4))
