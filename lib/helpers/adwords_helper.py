from .. import KeywordFetchingClass

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
    print(account_dummy_map)
    return account_dummy_map

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