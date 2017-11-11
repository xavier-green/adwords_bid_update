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

def fetch_adwords_data(client, service_name, fields, predicates, processing_function, version='v201710'):
    service = client.GetService(service_name, version=version)
    output = {}; offset = 0
    selector = {
      'fields': fields,
      'predicates':predicates,
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(self.page_size)
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
        offset += self.page_size
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])
    return output
