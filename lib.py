import re
import json
import urllib.request
import urllib.parse

# TODO: compile regular expressions ahead of search for faster results
# FUTURE: use `result = re.findall(r'topicid(\d+).*?>([\w\-\:\.\, ]+)?<', a)`
#       to get topics and their ids

ENDPOINTS = {
    'search'         : 'http://libgen.io/search.php',
    'api'            : 'http://libgen.io/json.php',
    'download'       : 'http://download1.libgen.io/ads.php',
    'direct_download': 'http://dl3.libgen.io/get.php'
}

FIELDS = [
  'title', 'filesize', 'author', 'pages', 'publisher', 'extension', 'md5'
]

def format_size(size):
    KB = 1024
    MB = KB * 1024
    GB = MB * 1024
    if size > GB:
        return '{:.2f} GB'.format(size / GB)
    elif size > MB:
        return '{:.2f} MB'.format(size / MB)
    elif size > KB:
        return '{:.2f} KB'.format(size / KB)
    else:
        return '{} B'.format(size)

def get_url(endpoint, **params):
  if params == {}:
    return endpoint
  else:
    return endpoint + '?' + urllib.parse.urlencode(params)

def get_response(endpoint, **params):
    url = get_url(endpoint, **params)
    request  = urllib.request.Request(url)
    return urllib.request.urlopen(request).read().decode('utf-8')

def get_books_ids(title, page, results=50):
    params = {
        # the search query
        'req'   : title,
        # number of results to view
        'res'   : results,
        # only display simple description of results
        'view'  : 'simple',
        # I have no idea what that is but leave it as it is
        'phrase': 1,
        # search in the default column field, other possible values
        # include title, isbn, md5, ...
        'column': 'def',
        # load results from page `page`
        'page'  : page
    }

    response = get_response(ENDPOINTS['search'], **params)
    ids = re.findall(r'<tr.*?><td>(\d+)', response)
    num = re.search(r'(\d+) books found', response)
    if num is not None:
    	num = int(num.groups()[0])
    else:
        # TODO this is actually an error and should be handled
        # differently, possibly raising an error, or return an
        # error code.
    	num = 0
    return ids, num

def get_books_meta_by_ids(ids, fields=None, load=True):
    if fields is None:
        fields = FIELDS

    params = {'ids': ','.join(ids), 'fields': ','.join(fields)}
    res = get_response(ENDPOINTS['api'], **params)
    return json.loads(res) if load else res

def get_download_key(md5):
    res = get_response(ENDPOINTS['download'], md5=md5)
    return re.findall('&key=([^\'"]*)', res)[0]

def get_books_meta(title, page):
  ids, num = get_books_ids(title, page)
  if ids == []:
    return []
  books = get_books_meta_by_ids(ids)
  
  for book in books:
    book['filesize'] = format_size(int(book['filesize']))
  
  return books, num

def get_book_url(md5):
  key = get_download_key(md5)
  return get_url(ENDPOINTS['direct_download'], md5=md5, key=key)
