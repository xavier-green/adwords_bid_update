#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, 'fr-FR')

from googleads import adwords
import os
import multiprocessing as mp

from .helpers import adwords_helper
import json

UPDATE_LOG = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'cache', 'bids_updated.csv')

class BidUpdate:

    def __init__(self, manual_account_id="392-078-0567", processes=4):
        self.manual_account_id = manual_account_id
        self.client = self.connect()
        self.processes = processes

    def update_all_bids(self, bid_update_map):
        processes = []
        pool = mp.Pool(processes=self.processes)
        account_id = self.manual_account_id
        for adgroupid in bid_update_map:
            processes.append(pool.apply_async(adwords_helper.update_bids, args=(account_id, adgroupid, bid_update_map[adgroupid], )))
        results = [req.get() for req in processes]
        results = "".join(results)
        with open(UPDATE_LOG, 'w') as fp:
            json.dump(results, fp)
        return("Done")

    def connect(self, manual_account_id=None):
        adwords_client = adwords.AdWordsClient.LoadFromStorage()
        if manual_account_id:
            adwords_client.SetClientCustomerId(manual_account_id)
        else:
            adwords_client.SetClientCustomerId(self.manual_account_id)
        return adwords_client
