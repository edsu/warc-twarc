#!/usr/bin/env python

import csv
import sys
import json

from twarc import Twarc
from twarc import json2csv
from bs4 import BeautifulSoup
from warcio.archiveiterator import ArchiveIterator

def extract_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    for div in soup.find_all('div', class_='tweet'):
        yield div.attrs.get('data-tweet-id')

def extract_javascript(content):
    content = content.decode('utf-8')
    data = json.loads((content))
    for tweet_id in extract_html(data.get('items_html', '')):
        yield tweet_id

def tweet_ids(warc_file):
    for record in ArchiveIterator(open(warc_file, 'rb')):
        if record.rec_type == 'response':
            
            url = record.rec_headers.get_header('WARC-Target-URI')
            content = record.content_stream().read()
        
            if url.startswith('https://twitter.com/search?q='):
                for tweet_id in extract_html(content):
                    yield tweet_id
            
            elif url.startswith('https://twitter.com/i/search/timeline?'):
                for tweet_id in extract_javascript(content):
                    yield tweet_id

def main(warc_file):
    twitter = Twarc()
    out = csv.writer(sys.stdout)
    out.writerow(json2csv.get_headings())
    for tweet in twitter.hydrate(tweet_ids(warc_file)):
        out.writerow(json2csv.get_row(tweet))

if __name__ == "__main__":
    main(sys.argv[1])
