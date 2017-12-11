#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, 'fr-FR')

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import httplib2
import os

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'credentials/client_secret.json'
APPLICATION_NAME = 'Mozart DE Sync Sheet'
SPREADSHEET_ID = '1yluHUk3xsHCzRTUm679gcLP5K2TcxEoPN-IfHywgYKg'
import json

class Spreadsheet:

    def __init__(self):
        self.client = self.connect()
        self.dummy_accounts = self.get_dummy_accounts()

    def get_manual_keywords_data(self, dummy_map):
        rangeName = 'kwmap!A:E'
        nlbe = 'nlbe!A:E'
        values = []
        # result = self.client.spreadsheets().values().get(
        #     spreadsheetId=SPREADSHEET_ID, range=rangeName).execute()
        # values = result.get('values', [])[1:]
        # print("Found", len(values), "rows in first mozart sheet")
        result = self.client.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=rangeName).execute()
        values = result.get('values', [])[1:]
        keyword_map = {}
        print("Found", len(values), "rows in both mozart sheet")
        log_str = ""
        for row in values:
            try:
                dummy = row[0]; mt = row[1]; kw = row[2]; adgroup = row[3]; campaign = row[4]
                log_str += dummy+";"+mt+";"+kw+";"+adgroup+";"+campaign+"\n"
            except:
                print(row)
                break;
            if (adgroup not in keyword_map):
              keyword_map[adgroup] = {}
            if (kw not in keyword_map[adgroup]):
              keyword_map[adgroup][kw] = {}
            if (mt not in keyword_map[adgroup][kw]):
              keyword_map[adgroup][kw][mt] = {}
            if ((dummy in dummy_map) and (mt in dummy_map[dummy])):
              bid = dummy_map[dummy][mt]['bid']
              url = dummy_map[dummy][mt]['url']
              keyword_map[adgroup][kw][mt] = {
                'bid': bid,
                'url': url,
                'campaign': campaign
              }
            else:
              keyword_map[adgroup][kw][mt] = {
                'bid': 500000,
                'url': None
              }
        return(keyword_map)

    def get_dummy_accounts(self):
        print("Fetching dummy accounts...")
        rangeName = 'accountlist!A:A'
        result = self.client.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=rangeName).execute()
        values = result.get('values', [])
        accounts = [row[0] for row in values][1:]
        print("Found",len(accounts),"accounts:",",".join(accounts))
        return(accounts)

    def connect(self):
        print("Creating google spreadsheet service...")
        credentials = self.get_sheets_credentials()
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
        return discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    def get_sheets_credentials(self):
        home_dir = os.path.dirname(os.path.realpath(__file__))
        credential_dir = os.path.join(home_dir, '..', 'credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'mozart_credentials.json')
        client_secret_path = os.path.join(credential_dir, 'client_secret.json')
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            credentials = tools.run_flow(flow, store)
        return credentials
