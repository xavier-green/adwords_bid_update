import requests
import pandas as pd
import os

url = "https://s3.amazonaws.com/bidgroup-dumps/syncsheet.xlsx"

XL_CACHE = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'cache', 'dummy_sheet.xls')

class Bucket:

    def __init__(self):
        self.xl = self.get_excel()
        self.dummy_accounts = self.get_dummy_accounts()
        print('Accounts:', self.dummy_accounts)

    def get_excel(self):
        print("Downloading sheet...")
        resp = requests.get(url)
        with open(XL_CACHE, 'wb') as output:
            output.write(resp.content)
        print("Done")
        return pd.ExcelFile(XL_CACHE)

    def get_dummy_accounts(self):
        accounts = self.xl.parse('accounts')
        return accounts['account'].values

    def get_manual_keywords_data(self, dummy_map):
        dummy_data = self.xl.parse('kwmap')
        keyword_map = {}
        print("Found", dummy_data.shape[0], "rows in mozart sheet")
        dummy_data = dummy_data.values
        log_str = ""
        for row in dummy_data:
            try:
                dummy = row[0]; mt = row[1]; kw = str(row[2]); adgroup = row[3]; campaign = row[4] #kw with str because of int keywords..
                log_str += str(dummy)+";"+str(mt)+";"+kw+";"+str(adgroup)+";"+str(campaign)+"\n"
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
            except:
                print("Error with row:",row)
        return(keyword_map)

if __name__ ==  '__main__':
    bucket = Bucket()
    dummy_map = bucket.get_manual_keywords_data({})
    print(dummy_map)
