import pandas as pd
from collections import defaultdict
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def connect_to_sheet(sheet_name):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open(sheet_name).sheet1

    # Extract and print all of the values
    # list_of_hashes = sheet.get_all_records()
    # print(list_of_hashes)
    return sheet


test_sheet = connect_to_sheet("SportsPedia NCAA Football Team Links")