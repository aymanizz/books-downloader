#!/usr/bin/python3

import re
import json
import urllib.request
import urllib.parse

import constants
from utils import (
    retryable,
    format_size,
    format_filename,
    generate_filename
)

def log_info(*args, **kwargs):
    print('[INFO] ', end='')
    print(*args, **kwargs)

def get_input(*args, **kwargs):
    print('[INPUT] ', end='')
    return input(*args, **kwargs)

@retryable(
    lambda: 'yes',
    lambda: exit(1),
    lambda: log_info('could not complete request.', 'retrying...')
)
def get_response(endpoint, params=None, headers=None):
    if headers is None:
        headers = {}
    if params is None:
        url = endpoint
    else:
        url = endpoint + '?' + urllib.parse.urlencode(params)

    log_info(url)
    request  = urllib.request.Request(url, None, headers)
    return urllib.request.urlopen(request)

def get_books_ids(title, results=100):
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
        'column': 'def'
    }

    log_info('loading page...')
    response = get_response(constants.ENDPOINTS['search'], params)
    content = response.read().decode('utf-8')
    ids = re.findall('<tr.*?><td>(\d+)', content)
    return ids

def get_books_meta(ids, fields=None):
    if fields is None:
        fields = constants.FIELDS

    params = {'ids': ','.join(ids), 'fields': ','.join(fields)}
    log_info('getting meta data...')
    res = get_response(constants.ENDPOINTS['api'], params)
    return json.loads(res.read().decode('utf-8'))

def get_download_key(md5):
    res = get_response(constants.ENDPOINTS['download'], {'md5': md5})
    return re.findall('&key=([^\'"]*)', res.read().decode('utf-8'))[0]

@retryable(
    lambda: 'yes',
    lambda: None,
    lambda: log_info('could not complete download', 'retrying...')
)
def download_file(res, filename, filesize=-1):
    with open(filename, 'wb') as file:
        chunk_size = 16 * 1024
        downloaded_size = 0
        of_size = ' of ' + format_size(filesize) if filesize else ''
        while True:
            chunk = res.read(chunk_size)
            if not chunk:
                break
            downloaded_size += len(chunk)
            file.write(chunk)
            info = format_size(downloaded_size) + of_size
            log_info('downloaded ' + info + '...\r', end='')
        if downloaded_size < filesize:
            raise Exception
        log_info(
            'download complete :: downloaded {} :: saved to:\n\t{}'.format(
                format_size(downloaded_size), filename
            ))

def download_book(book):
    log_info('generating download url...')
    params = {'key': get_download_key(book['md5']), 'md5': book['md5']}
    filename = generate_filename(book['title'], book['extension'])
    res = get_response(constants.ENDPOINTS['direct_download'], params)
    log_info('downloading...')
    download_file(res, filename, book['filesize'])

def main():
    try:
        while True:
            title = get_input('book title: ')
            if len(title) >= 3:
                break
            log_info('book title must contain at least 3 characters')
        ids = get_books_ids(title)
        if ids == []:
            return
        books = get_books_meta(ids)
        num_of_books = len(ids)
        log_info('found', num_of_books, 'books', '\n')
        if num_of_books == 0:
            return

        for index, book in enumerate(books):
            book['filesize'] = int(book['filesize'])
            book['size']     = format_size(book['filesize'])
            print('{:2}) Book info: {{'.format(index))
            for key in ['title', 'author', 'pages', 'extension', 'size']:
                print('\t{:<10.10} | {:<.70}'.format(key, book[key]))
            print('}\n', constants.SEPERATOR, sep='')
        
        while True:
            try:
                choice = int(get_input('Book choice: '))
                if choice >= min(num_of_books, 100) or choice < 0:
                    raise ValueError
            except ValueError:
                log_info('input must be in range(0, {})'.format(
                    min(num_of_books, 100)))
                continue
            book = books[choice]
            download_book(book)
            break
    except (KeyboardInterrupt, EOFError):
        print('\n[QUIT]')


if __name__ == '__main__':
    main()