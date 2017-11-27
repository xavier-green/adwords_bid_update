#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, 'fr-FR')

from googleads import adwords
import os
import multiprocessing as mp

from .helpers import adwords_helper
import json
import time

UPDATE_LOG = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'cache', 'bids_updated.csv')

class BidUpdate:

    def __init__(self, manual_account_id="392-078-0567", processes=4):
        self.manual_account_id = manual_account_id
        self.client = self.connect()
        self.processes = processes

    def update_all_bids(self, bid_update_map):
        processes = []
        max_l = 2000
        pool = mp.Pool(processes=self.processes)
        account_id = self.manual_account_id
        print('found',len(list(bid_update_map.keys())))
        total_splits = []
        for adgroupid in bid_update_map:
            sub_bid_update = bid_update_map[adgroupid]
            keyword_keys = list(sub_bid_update.keys())
            n_keys = len(keyword_keys)
            print(n_keys,'keys')
            splits = list(set([int(i/max_l) for i in range(n_keys)]))
            splits = [max_l*(1+x) for x in splits]
            previous_split = 0
            sub_bid_update = sub_bid_update.items()
            for split in splits:
                submap = {key: value for i, (key, value) in enumerate(sub_bid_update) if i <= split and i > previous_split}
                processes.append(pool.apply_async(adwords_helper.update_bids, args=(account_id, adgroupid, submap, )))
                previous_split = split
                total_splits.append(submap)
                time.sleep(30)
        results = [req.get() for req in processes]
        for i,result in enumerate(results):
            if 'isFault' in  result:
                if result['isFault']:
                    self.refreshIfError(total_splits[i])
        # results = "".join(results)
        # with open(UPDATE_LOG, 'w') as fp:
        #     json.dump(results, fp)
        return("Done")

    def refreshIfError(self, split, attempts=3):
        print("refresh because of error")
        if attempts==0:
            print("Error after 3 refresh")
            return None
        resp = adwords_helper.update_bids, args=(account_id, adgroupid, submap, )
        if 'isFault' in  resp:
            if resp['isFault']:
                time.sleep(120)
                self.refreshIfError(total_splits[i], attempts-1)



    def connect(self, manual_account_id=None):
        adwords_client = adwords.AdWordsClient.LoadFromStorage()
        if manual_account_id:
            adwords_client.SetClientCustomerId(manual_account_id)
        else:
            adwords_client.SetClientCustomerId(self.manual_account_id)
        return adwords_client
