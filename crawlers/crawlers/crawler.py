#!/usr/bin/python3

from sys import argv;
from urllib import request;
from urllib.request import Request;

# check for URL to crawl
if len(argv) != 2:
    print('ERROR: Expected to get URL to crawl');
    exit(1);

# special headers
req_headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'
};

# prepare the initial request
initial_request = Request(argv[1], headers=req_headers);
# try to fetch the page
resp = request.urlopen(initial_request);
# check if the server likes us
if resp.status != 200:
    resp.close();
    raise RuntimeError('Server denied our connection with {0}: {1}'.format(resp.status, resp.reason));
print('Server accepted our connection with {0}: {1}'.format(resp.status, resp.reason));
# validate for Content-Type
con_type = resp.getheader('Content-Type');
if 'text/html' not in con_type:
    #raise ValueError('Content-Type "{0}" of response says this is not a HTML response'.format(con_type));
    print('Content-Type "{0}" of response says this is not a HTML response'.format(con_type));
if 'charset=UTF-8' not in con_type:
    #raise ValueError('Content-Type "{0}" of response says this page is not UTF-8 encoded'.format(con_type));
    print('Content-Type "{0}" of response says this page is not UTF-8 encoded'.format(con_type));
# read the response into text
resp_html = resp.read().decode('utf-8');
# close the connection
resp.close();

# remove the start of the page until <body
# to make parsing easier
body_start = resp_html.find('<body');
resp_body = resp_html[body_start:];

# find the title of the chapter
title_start = resp_body.find('<h1 class="entry-title">');
if title_start == -1:
    raise RuntimeError('Unable to find start of Chapter Title');
title_end = resp_body.find('</h1>', title_start);
if title_end == -1:
    raise RuntimeError('Unable to find end of Chapter Title');
title_end += 5; # also get the closing tag
# start getting the content with the title
post_content = resp_body[title_start:title_end];
# also add a horizontal line for style points
post_content += '<hr/>'

# find the start of the content
content_start = resp_body.find('<div class="entry-content hentry-container"');
if content_start == -1:
    raise RuntimeError('Unable to find start of content');
# find the first div
content_end = resp_body.find('<div', content_start+10);
if content_end == -1:
    raise RuntimeError('Unable to find div that shows end of content');
# get the content
post_content += resp_body[content_start:content_end];
# close the content div
post_content += '</div>';

# add a closing ***
post_content += '<p>* * *</p>'

# write the chapter to tmp
f = open('/tmp/t.html', 'w');
f.write(post_content);
f.close();
