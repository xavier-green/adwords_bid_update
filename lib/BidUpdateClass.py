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
        # with open(UPDATE_LOG, 'w') as fp:
        #     json.dump(results, fp)
        return("Done")



    def connect(self, manual_account_id=None):
        adwords_client = adwords.AdWordsClient.LoadFromStorage()
        if manual_account_id:
            adwords_client.SetClientCustomerId(manual_account_id)
        else:
            adwords_client.SetClientCustomerId(self.manual_account_id)
        return adwords_client
