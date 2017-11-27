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

    # Initialization of the spreadsheet, containing manual account IDs and dummy placeholders
    mozart_sheet = Spreadsheet()
    dummy_accounts = mozart_sheet.dummy_accounts

    # We then create a dictionnary mapping the dummy placeholders to their udpated bid
    adwords_keywords = KeywordFetch()
    dummy_map = adwords_keywords.get_dummy_map(dummy_accounts)

    bid_updater = BidUpdate()

    keywords_to_update_map = mozart_sheet.get_manual_keywords_data(dummy_map)

    # To fetch actual keywords, we will crawl the relevant adgroups where they are situated
    adgroup_map = adwords_keywords.adgroup_map
    adgroups_to_update_map = [{'name':adgroup, 'id':adgroup_map[adgroup]} for adgroup in keywords_to_update_map.keys()]
    print(adgroups_to_update_map)

    # Updating a keyword is done from the keyword ID, not the actual text, so we pull the relevant IDs
    keyword_ids_map = adwords_keywords.get_keyword_ids_map(adgroups_to_update_map)

    # We create the bid update dict of the sort: adgroup_id -> keyword_id -> new bid
    bid_update_map = adwords_keywords.generate_bid_update_map(adgroups_to_update_map, keywords_to_update_map, keyword_ids_map)

    # We update the bids
    bid_updater.update_all_bids(bid_update_map)
