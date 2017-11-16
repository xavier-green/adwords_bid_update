#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, 'fr-FR')

import multiprocessing as mp
import time
import json
import os.path

from lib.SpreadsheetClass import Spreadsheet
from lib.KeywordFetchingClass import KeywordFetch
from lib.BidUpdateClass import BidUpdate


if __name__ ==  '__main__':

    mozart_sheet = Spreadsheet()
    dummy_accounts = mozart_sheet.dummy_accounts

    adwords_keywords = KeywordFetch()
    dummy_map = adwords_keywords.get_dummy_map(dummy_accounts)

    bid_updater = BidUpdate()

    keywords_to_update_map = mozart_sheet.get_manual_keywords_data(dummy_map)

    adgroup_map = adwords_keywords.adgroup_map
    adgroups_to_update_map = [{'name':adgroup, 'id':adgroup_map[adgroup]} for adgroup in keywords_to_update_map]
    print(adgroups_to_update_map)

    keyword_ids_map = adwords_keywords.get_keyword_ids_map(adgroups_to_update_map)

    bid_update_map = adwords_keywords.generate_bid_update_map(adgroups_to_update_map, keywords_to_update_map, keyword_ids_map)

    bid_updater.update_all_bids(bid_update_map)

    # t = bidupdate.update_bid(ManualAccountId, 49438350129, {"297428045495": 800000, "13426016": 800000, "295559809102": 800000, "28188396": 800000, "294772863026": 800000})
