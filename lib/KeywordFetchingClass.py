#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, 'fr-FR')

from googleads import adwords
import os
import json

from .helpers import adwords_helper
import multiprocessing as mp

ADGROUP_CACHE = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'cache', 'adgroup_cache.json')
KEYWORDS_IDS_CACHE = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'cache', 'keyword_cache.json')
BID_ERROR_CACHE = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'cache', 'bid_error_cache.json')

class KeywordFetch:

    def __init__(self,
                page_size=1000,
                manual_account_id="392-078-0567",
                adgroup_from_cache=False,
                keyword_ids_from_cache=False,
                processes=4):
        self.clients_dict = {} #Since we are pulling data from multiple accounts, keep track of their clients here
        self.page_size = page_size
        self.processes = processes
        self.keyword_ids_from_cache = keyword_ids_from_cache
        self.adgroup_from_cache = adgroup_from_cache
        self.manual_account_id = manual_account_id
        self.adgroup_map = self.get_adgroup_map()

    def generate_bid_update_map(self, adgroup_ids, keywords_to_update_map, keyword_id_map):
        print("Generating bid update map...")
        bid_update_map = {}
        bid_error_kw = []
        for adgroup in adgroup_ids:
            adgroup_id = adgroup['id']
            adgroup_name = adgroup['name']
            for keyword in keywords_to_update_map[adgroup_name]:
                for mt in keywords_to_update_map[adgroup_name][keyword]:
                    bid = keywords_to_update_map[adgroup_name][keyword][mt]['bid']
                    # campaign = keywords_to_update_map[adgroup_name][keyword][mt]['campaign']
                    keyword_clean = keyword.replace("[","").replace("]","")
                    if ((keyword_clean in keyword_id_map[adgroup_name]) and (mt in keyword_id_map[adgroup_name][keyword_clean])):
                        # print(keyword_id_map[adgroup_name][keyword_clean])
                        keyword_id = keyword_id_map[adgroup_name][keyword_clean][mt]
                        if adgroup_id not in bid_update_map:
                            bid_update_map[adgroup_id] = {}
                        if keyword_id not in bid_update_map[adgroup_id]:
                            bid_update_map[adgroup_id][keyword_id] = {}
                        bid_update_map[adgroup_id][keyword_id] = {
                            'bid': bid,
                            # 'campaign': campaign,
                            'adgroup_name': adgroup_name,
                            'keyword': keyword
                        }
                    else:
                        bid_error_kw.append({
                            'keyword': keyword,
                            'adgroup': adgroup_name
                        })
        with open(BID_ERROR_CACHE, 'w') as fp:
            json.dump(bid_error_kw, fp)
        return bid_update_map

    def get_keyword_ids_map(self, adgroup_ids):
        print("Getting keyword id map...")
        if (self.keyword_ids_from_cache and os.path.isfile(KEYWORDS_IDS_CACHE)):
            print("Fetching from cache")
            with open(KEYWORDS_IDS_CACHE) as fp:
                keyword_id_map = json.load(fp)
                return keyword_id_map
        keyword_id_requests = []
        pool = mp.Pool(processes=self.processes)
        for adgroup in adgroup_ids:
            account_id = self.manual_account_id
            page_size = self.page_size
            keyword_id_requests.append(pool.apply_async(adwords_helper.get_adgroup_keyword_ids_map, args=(account_id, adgroup, page_size, )))
        keywords_response = [req.get() for req in keyword_id_requests]
        pool = None
        keyword_id_map = keywords_response.pop()
        for el in keywords_response:
            keyword_id_map.update(el)
        with open(KEYWORDS_IDS_CACHE, 'w') as fp:
            json.dump(keyword_id_map, fp)
        return keyword_id_map

    def get_adgroup_map(self):
        print("Getting adgroup mapping...")
        if (self.adgroup_from_cache and os.path.isfile(ADGROUP_CACHE)):
            print("Fetching from cache")
            with open(ADGROUP_CACHE) as data_file:
                data = json.load(data_file)
            return data
        service_name = 'AdGroupService'
        fields = ['Id', 'Name']
        predicates = [{
            'field': 'Status',
            'operator': 'EQUALS',
            'values': ['ENABLED']
        }]
        # client = self.connect(self.manual_account_id)
        def processing_function(element, output):
            ad_group_name = element['name']
            ad_group_id = element['id']
            if (ad_group_name not in output):
                output[ad_group_name] = {}
            output[ad_group_name] = ad_group_id
            return output
        ad_group_map = adwords_helper.fetch_adwords_data(self.manual_account_id, service_name, fields, predicates, processing_function, self.page_size)
        with open(ADGROUP_CACHE, 'w') as fp:
            json.dump(ad_group_map, fp)
        print("Found",len(ad_group_map.keys()),"adgroups")
        return ad_group_map

    def get_dummy_map(self, dummy_accounts):
        print("Getting dummy map...")
        pool = mp.Pool(processes=self.processes)
        processes = []
        print(dummy_accounts)
        for dummy_account in dummy_accounts:
            page_size = self.page_size
            processes.append(pool.apply_async(adwords_helper.get_account_dummy_keywords, args=(dummy_account, page_size, )))
        results = [req.get() for req in processes]
        dummy_map = results.pop()
        for dummy_object in results:
            dummy_map.update(dummy_object)
        pool = None
        return dummy_map

    def connect(self, customer_id):
        if (self and (customer_id in self.clients_dict)):
            return self.clients_dict[customer_id]
        adwords_client = adwords.AdWordsClient.LoadFromStorage()
        adwords_client.SetClientCustomerId(customer_id)
        if self:
            self.clients_dict[customer_id] = adwords_client
        return adwords_client
