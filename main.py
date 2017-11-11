#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, 'fr-FR')

import sheets
import keywords
import adgroups
import bidupdate
import multiprocessing as mp
import time
import json
import os.path

from lib.SpreadsheetClass import Spreadsheet
from lib.KeywordFetchingClass import KeywordFetch
from lib.BidUpdateClass import BidUpdate

ManualAccountId = "392-078-0567"
spreadsheets_service = sheets.connect_to_spreadsheet()

ADGROUP_MAP_LOCATION = 'data/adgroup_map.json'
KEYWORD_IDS_MAP_LOCATION = 'data/keyword_id_map.json'
KEYWORD_ERROR_LOCATION = 'data/keyword_errors.json'

def get_adgroup_map(open_file=False):
    if (open_file and os.path.isfile(ADGROUP_MAP_LOCATION)):
        with open(adgroupjson) as data_file:
            data = json.load(data_file)
        return data
    adgroup_map = adgroups.get_adgroups(ManualAccountId)
    with open(ADGROUP_MAP_LOCATION, 'w') as fp:
        json.dump(adgroup_map, fp)
    return adgroup_map

def get_dummy_map():
    dummy_accounts = sheets.getAccounts(spreadsheets_service)
    print(dummy_accounts)
    pool = mp.Pool(processes=4)
    results = pool.map_async(keywords.get_account_keywords, dummy_accounts)
    results = results.get()
    dummy_map = results.pop()
    for dummy_object in results:
        dummy_map.update(dummy_object)
    pool = None
    return dummy_map

def get_keyword_to_update(dummy_map):
    keyword_map = sheets.getKeywordData(spreadsheets_service, dummy_map)
    return keyword_map

def get_keyword_ids(adgroup_ids, adgroup_map, keyword_map, open_file=False):
    if (open_file and os.path.isfile(KEYWORD_IDS_MAP_LOCATION)):
        with open(KEYWORD_IDS_MAP_LOCATION) as fp:
            keyword_id_map = json.load(fp)
            return keyword_id_map
    keyword_id_requests = []
    pool = mp.Pool(processes=4)
    for adgroup in adgroup_ids:
        keyword_id_requests.append(pool.apply_async(keywords.get_manual_account, args=(ManualAccountId, adgroup, )))
    keywords_response = [req.get() for req in keyword_id_requests]
    keyword_id_map = keywords_response.pop()
    for el in keywords_response:
        keyword_id_map.update(el)
    with open(KEYWORD_IDS_MAP_LOCATION, 'w') as fp:
        json.dump(keyword_id_map, fp)
    return keyword_id_map

def get_bid_update_file(adgroup_ids, keyword_to_update_map, keyword_id_map):
    bid_update_map = {}
    bid_error_kw = []
    for adgroup in adgroup_ids:
        adgroup_id = adgroup['id']
        adgroup_name = adgroup['name']
        for keyword in keyword_to_update_map[adgroup_name]:
            for mt in keyword_to_update_map[adgroup_name][keyword]:
                bid = keyword_to_update_map[adgroup_name][keyword][mt]['bid']
                keyword_clean = keyword.replace("[","").replace("]","")
                if ((keyword_clean in keyword_id_map[adgroup_name]) and (mt in keyword_id_map[adgroup_name][keyword_clean])):
                    # print(keyword_id_map[adgroup_name][keyword_clean])
                    keyword_id = keyword_id_map[adgroup_name][keyword_clean][mt]
                    if adgroup_id not in bid_update_map:
                        bid_update_map[adgroup_id] = {}
                    if keyword_id not in bid_update_map[adgroup_id]:
                        bid_update_map[adgroup_id][keyword_id] = {}
                    bid_update_map[adgroup_id][keyword_id] = bid
                else:
                    bid_error_kw.append({
                        'keyword': keyword,
                        'adgroup': adgroup_name
                    })
    with open(KEYWORD_ERROR_LOCATION, 'w') as fp:
        json.dump(bid_error_kw, fp)
    with open('bidupdate.json', 'w') as fp:
        json.dump(bid_update_map, fp)
    return bid_update_map

def update_all_bids(bid_update_map):
    processes = []
    pool = mp.Pool(processes=4)
    for adgroupid in bid_update_map:
        processes.append(pool.apply_async(bidupdate.update_bid, args=(ManualAccountId, adgroupid, bid_update_map[adgroupid], )))
        # for keywordid in bid_update_map[adgroupid]:
        #     newbid = bid_update_map[adgroupid][keywordid]
        #     processes.append(pool.apply_async(bidupdate.update_bid, args=(ManualAccountId, adgroupid, keywordid, newbid)))
    results = [req.get() for req in processes]
    with open('data/output.json', 'w') as fp:
        json.dump(results, fp)
    return("Done")



if __name__ ==  '__main__':

    mozart_sheet = Spreadsheet()
    dummy_accounts = mozart_sheet.dummy_accounts

    adwords_keywords = KeywordFetch()
    dummy_map = adwords_keywords.get_dummy_map(dummy_accounts)

    bid_updater = BidUpdate()

    keywords_to_update_map = mozart_sheet.get_manual_keywords_data(dummy_map)

    adgroup_map = adwords_keywords.adgroup_map
    adgroups_to_update_map = [{'name':adgroup, 'id':adgroup_map[adgroup]} for adgroup in keyword_to_update_map]

    keyword_ids_map = adwords_keywords.get_keyword_ids_map(adgroups_to_update_map)

    bid_update_map = adwords_keywords.generate_bid_update_map(adgroups_to_update_map, keywords_to_update_map, keyword_ids_map)

    bid_updater.update_all_bids(bid_update_map)

    # t = bidupdate.update_bid(ManualAccountId, 49438350129, {"297428045495": 800000, "13426016": 800000, "295559809102": 800000, "28188396": 800000, "294772863026": 800000})
    # print(done)

    # start = time.time()
    # adgroup_map = get_adgroup_map()
    # end = time.time()
    # print("\nAdgroup map took", -(start-end)/60,"minutes")
    #
    # start = time.time()
    # dummy_map = get_dummy_map()
    # end = time.time()
    # print("\nDummy map took", -(start-end)/60,"minutes")
    #
    # start = time.time()
    # keyword_to_update_map = get_keyword_to_update(dummy_map)
    # end = time.time()
    # print("\nKeyword to update map took", -(start-end)/60,"minutes")
    #
    # adgroup_ids = [{'name':adgroup, 'id':adgroup_map[adgroup]} for adgroup in keyword_to_update_map]
    # print(adgroup_ids)
    #
    # start = time.time()
    # keyword_id_map = get_keyword_ids(adgroup_ids, adgroup_map, keyword_to_update_map)
    # end = time.time()
    # print("\nKeyword id map took", -(start-end)/60,"minutes")
    #
    # start = time.time()
    # bid_update_map = get_bid_update_file(adgroup_ids, keyword_to_update_map, keyword_id_map)
    # end = time.time()
    # print("\nBid update map took", -(start-end)/60,"minutes")

    # with open('bidupdate.json') as fp:
    #     bid_update_map = json.load(fp)
    #
    # start = time.time()
    # done = update_all_bids(bid_update_map)
    # end = time.time()
    # print("\nUpdating bids took", -(start-end)/60,"minutes")



    # print(bid_error_kw)
