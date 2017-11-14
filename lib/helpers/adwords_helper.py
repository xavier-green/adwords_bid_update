from .. import KeywordFetchingClass, BidUpdateClass

DUMMY_KEYWORD_PREDICATES = [
    {
        'field': 'CriteriaType',
        'operator': 'EQUALS',
        'values': ['KEYWORD']
    },
    {
          'field': 'KeywordText',
          'operator': 'STARTS_WITH_IGNORE_CASE',
          'values': ['mzrtmk']
    },
    {
          'field': 'KeywordMatchType',
          'operator': 'NOT_EQUALS',
          'values': ['PHRASE']
    },
    {
          'field': 'Status',
          'operator': 'EQUALS',
          'values': ['ENABLED']
    }
]

def keyword_id_predicates(adgroupid):
    return [
        {
            'field': 'CriteriaType',
            'operator': 'EQUALS',
            'values': ['KEYWORD']
        },
        {
              'field': 'KeywordMatchType',
              'operator': 'NOT_EQUALS',
              'values': ['PHRASE']
        },
        {
              'field': 'AdGroupId',
              'operator': 'EQUALS',
              'values': [adgroupid]
        },
        {
              'field': 'Status',
              'operator': 'EQUALS',
              'values': ['ENABLED']
        }
    ]

def get_account_dummy_keywords(customer_id, page_size):
    service_name = 'AdGroupCriterionService'
    fields = ['Id', 'KeywordMatchType', 'KeywordText', 'CpcBid', 'FinalUrls']
    predicates = DUMMY_KEYWORD_PREDICATES
    def processing_function(element, output):
        keyword_text = element['criterion']['text']
        keyword_mt = element['criterion']['matchType']
        keyword_cpc = None
        for bid in element['biddingStrategyConfiguration']['bids']:
            bidtype = bid['Bids.Type']
            if bidtype=="CpcBid":
                keyword_cpc = bid['bid']['microAmount']
        keyword_url = element['finalUrls']['urls'][0]
        if keyword_text not in output:
            output[keyword_text] = {}
        output[keyword_text][keyword_mt] = {
            'bid': keyword_cpc,
            'url': keyword_url
        }
        return output
    account_dummy_map = fetch_adwords_data(customer_id, service_name, fields, predicates, processing_function, page_size)
    return account_dummy_map

def get_adgroup_keyword_ids_map(customer_id, adgroup, page_size):
    adgroup_id = adgroup['id']
    adgroup_name = adgroup['name']
    print("Fetching all keywords in", adgroup_name)
    service_name = 'AdGroupCriterionService'
    fields = ['Id', 'KeywordMatchType', 'KeywordText']
    predicates = keyword_id_predicates(adgroup_id)
    def processing_function(element, output):
        keyword_text = element['criterion']['text']
        keyword_mt = element['criterion']['matchType']
        keyword_id = element['criterion']['id']
        if keyword_text not in output:
            output[keyword_text] = {}
        if keyword_mt not in output[keyword_text]:
            output[keyword_text][keyword_mt] = {}
        output[keyword_text][keyword_mt] = keyword_id
        return output
    adgroup_keyword_ids_map = fetch_adwords_data(customer_id, service_name, fields, predicates, processing_function, page_size)
    print("Found",len(adgroup_keyword_ids_map.keys()),"keywords in",adgroup_name)
    adgroup_keyword_ids_map = {
        adgroup_name: adgroup_keyword_ids_map
    }
    return adgroup_keyword_ids_map

def fetch_adwords_data(customer_id, service_name, fields, predicates, processing_function, page_size, version='v201710'):
    client = KeywordFetchingClass.KeywordFetch.connect(None, customer_id)
    service = client.GetService(service_name, version=version)
    output = {}; offset = 0
    selector = {
      'fields': fields,
      'predicates':predicates,
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(page_size)
      }
    }
    more_pages = True
    while more_pages:
        page = service.get(selector)
        if 'entries' in page:
          for element in page['entries']:
              output = processing_function(element, output)
        else:
          print('No ad groups were found.')
        offset += page_size
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])
        more_pages = False
    return output

def create_bid_service(ad_group_id, criterion_id, newbid):
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

def update_bids(customer_id, adgroupid, adgroup_object):
    client = BidUpdateClass.BidUpdate.connect(None, customer_id)
    ad_group_criterion_service = client.GetService(
      'AdGroupCriterionService', version='v201710')
    operations = []
    tracking_map = {}
    for keywordid in adgroup_object:
       newbid = adgroup_object[keywordid]['bid']
       if round(newbid,0) != 0:
           if newbid == 500000:
               newbid = 100000
           operations.append(create_bid_service(adgroupid, keywordid, newbid))

    response = ad_group_criterion_service.mutate(operations)
    # print(response)
    if not response:
      print('Failed to process bid queue for',adgroupid)

    output = "" #[]
    if 'value' in response:
      for criterion in response['value']:
        if criterion['criterion']['Criterion.Type'] == 'Keyword':
          for bid in criterion['biddingStrategyConfiguration']['bids']:
              bidtype = bid['Bids.Type']
              if bidtype=="CpcBid":
                  k_id = criterion['criterion']['id']
                  output += adgroup_object[k_id]['adgroup_name']+";"+adgroup_object[k_id]['keyword']+";"+str(bid['bid']['microAmount'])+"\n";
                  # output.append({
                  #     'newbid':bid['bid']['microAmount'],
                  #     'adgroupid':adgroupid,
                  #     'keywordid':k_id,
                  #     'campaign': adgroup_object[k_id]['campaign'],
                  #     'adgroup_name': adgroup_object[k_id]['adgroup_name']
                  # })
    else:
      output.append(None)
      print('No ad group criteria were updated.')

    return output
