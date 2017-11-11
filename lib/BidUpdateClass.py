#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, 'fr-FR')

from googleads import adwords
import os

UPDATE_LOG = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'cache', 'keyword_cache.json')

class BidUpdate:

    def __init__(self, manual_account_id="392-078-0567", processes=4):
        self.client = self.connect()
        self.manual_account_id = manual_account_id
        self.processes = processes

    def update_all_bids(self, bid_update_map):
        processes = []
        pool = mp.Pool(processes=self.processes)
        for adgroupid in bid_update_map:
            processes.append(pool.apply_async(bidupdate.update_bid, args=(adgroupid, bid_update_map[adgroupid], )))
        results = [req.get() for req in processes]
        with open(UPDATE_LOG, 'w') as fp:
            json.dump(results, fp)
        return("Done")

    def update_bids(self, adgroupid, adgroup_object):
        ad_group_criterion_service = self.client.GetService(
          'AdGroupCriterionService', version='v201710')
        operations = []
        for keywordid in adgroup_object:
           newbid = adgroup_object[keywordid]
           if round(newbid,0) != 0:
               operations.append(create_bid_service(adgroupid, keywordid, newbid))

        response = ad_group_criterion_service.mutate(operations)
        # print(response)
        if not response:
          print('Failed to process bid queue for',adgroupid)

        output = []
        if 'value' in response:
          for criterion in response['value']:
            if criterion['criterion']['Criterion.Type'] == 'Keyword':
              for bid in criterion['biddingStrategyConfiguration']['bids']:
                  bidtype = bid['Bids.Type']
                  if bidtype=="CpcBid":
                      output.append({
                          'newbid':bid['bid']['microAmount'],
                          'adgroupid':adgroupid,
                          'keywordid':criterion['criterion']['id']
                      })
        else:
          output.append(None)
          print('No ad group criteria were updated.')

        return output

    def create_bid_service(self, ad_group_id, criterion_id, newbid):
        return {
            'operator': 'SET',
            'operand': {
                'xsi_type': 'BiddableAdGroupCriterion',
                'adGroupId': ad_group_id,
                'criterion': {
                    'id': criterion_id,
                },
                'biddingStrategyConfiguration': {
                    'bids': [
                        {
                            'xsi_type': 'CpcBid',
                            'bid': {
                                'microAmount': newbid
                            }
                        }
                    ]
                }
            }
        }

    def connect(self):
        adwords_client = adwords.AdWordsClient.LoadFromStorage()
        adwords_client.SetClientCustomerId(self.manual_account_id)
        return adwords_client
