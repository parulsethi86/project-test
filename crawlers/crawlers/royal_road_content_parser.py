from html.parser import HTMLParser;
from os import path;
from urllib.parse import urlparse;
from urllib import request;
from urllib.request import Request;

class ShiroContentParser(HTMLParser):
    """Parses the content section of https://shirotl.wordpress.com"""

    # headers to be used in a request
    req_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'
    };


    def __init__(self, url_file_path, target_directory, img_index = 1):
        # call the parent constructor
        super().__init__();
        # make sure we got a url file
        if str(type(url_file_path)) != str(type('')):
            raise ValueError('url_file_path must be string');
        if len(url_file_path) == 0:
            raise ValueError('url_file_path must have a positive length');
        if not path.isfile(url_file_path):
            raise ValueError('url_file_path does not point to a file');
        self.url_file = url_file_path;
        # make sure the given target directory exists
        if str(type(target_directory)) != str(type('')):
            raise ValueError('target_directory must be string');
        if len(target_directory) == 0:
            raise ValueError('target_directory must have a positive length');
        if not path.isdir(target_directory):
            raise ValueError('target_directory "{0}" is not a directory'.format(target_directory));
        self.target_directory = target_directory;
        # remove trailing '/' if it is there
        if target_directory[-1] == '/':
            target_directory = target_directory[0:len(target_directory)-1];
        # create a file to write the parsed content to
        self.output_file = open(target_directory + '/story.html', 'w');
        # determine which suffix to give the image
        self.image_index = img_index;
        # start the crawl
        #self.start_crawl();

    # === PARSER METHODS ===
    def handle_data(self, data):
        # just write the data
        self.output_file.write(data);

    def handle_endtag(self, tag):
        # ignore "a" tag
        if tag.lower() == 'a':
            return;
        # just write the end tag
        self.output_file.write('</{0}>'.format(tag));

    def handle_startendtag(self, tag, attrs):
        # ignore "a" tag
        if tag.lower() == 'a':
            return;
        # write based on attribute count
        if len(attrs) == 0:
            # no attributes so just write the start tag
            self.output_file.write('<{0}/>'.format(tag));
        elif tag == 'img':
            # got a img tag write it
            self.output_file.write('<{0} '.format(tag));
            # then write the attributes
            attr_list = [];
            for attr in attrs:
                # but ignore the ID tag
                if attr[0] == 'id':
                    continue;
                elif attr[0] == 'src':
                    # fetch the original image
                    image_file_name = self.download_image(attr[1]);
                    # note its name down
                    attr_list.append('src="{0}"'.format(image_file_name));
                    continue;
                attr_list.append('{0}="{1}"'.format(attr[0], attr[1]));
            self.output_file.write(' '.join(attr_list));
            # then close the tag
            self.output_file.write('/>');
        else:
            # first write the tag
            self.output_file.write('<{0} '.format(tag));
            # then write the attributes
            attr_list = [];
            for attr in attrs:
                # but ignore the ID tag
                if attr[0] == 'id':
                    continue;
                attr_list.append('{0}="{1}"'.format(attr[0], attr[1]));
            self.output_file.write(' '.join(attr_list));
            # then close the tag
            self.output_file.write('/>');

    def handle_starttag(self, tag, attrs):
        # ignore "a" tag
        if tag.lower() == 'a':
            return;
        # write based on attribute count
        if len(attrs) == 0:
            # no attributes so just write the start tag
            self.output_file.write('<{0}>'.format(tag));
        else:
            # first write the tag
            self.output_file.write('<{0} '.format(tag));
            # then write the attributes
            attr_list = [];
            for attr in attrs:
                # but ignore the ID and class tag
                if attr[0] == 'id' or attr[0] == 'class':
                    continue;
                attr_list.append('{0}="{1}"'.format(attr[0], attr[1]));
            self.output_file.write(' '.join(attr_list));
            # then close the tag
            self.output_file.write('>');

    # === HELPER FUNCTIONS ===
    def complete_url(self, url_path):
        """Extends a url path with the given crawl url to a
        full url

        :param url_path: The url path to extent
        :type url_path: str
        """
        # check if this really is a path
        if url_path[0] != '/':
            return url_path;
        # split the orginal url
        split_url = urlparse(self.crawl_url);
        # return the new url
        return '{0}://{1}{2}'.format(split_url.scheme, split_url.netloc, url_path);

    def fetch_content(self, url):
        """Fetches the content from a http://japtem.com/ post
        and wrings it through the parser

        :param url: The url from which to fetch
        :type url: str
        """
        print('Trying to crawl content at: {0}'.format(url));
        # prepare the initial request
        initial_request = Request(url, headers=self.req_headers);
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
        if 'charset=UTF-8' not in con_type and 'charset=utf-8' not in con_type:
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
        title_start = resp_body.find('<h1');
        if title_start == -1:
            raise RuntimeError('Unable to find start of Chapter Title');
        title_end = resp_body.find('</h1>', title_start);
        if title_end == -1:
            raise RuntimeError('Unable to find end of Chapter Title');
        title_end += 5; # also get the closing tag
        # start getting the content with the title
        post_content = resp_body[title_start:title_end];
        # also add a horizontal line for style points
        post_content += '<hr/>';

        # find the start of the content
        content_start = resp_body.find('<div class="chapter-inner chapter-content"');
        if content_start == -1:
            raise RuntimeError('Unable to find start of content');
        # find the first div
        content_end = resp_body.find('<h6 class="bold uppercase text-center">Advertisement</h6>', content_start+10);
        if content_end == -1:
            raise RuntimeError('Unable to find "Advertisement" that shows end of content');
        # get the content
        post_content += resp_body[content_start:content_end];
        # close the content div
        post_content += '</div>';

        # add a closing ***
        post_content += '<p>* * *</p>';
        # feed the content to the parser
        self.feed(post_content);

    def download_image(self, url):
        """Download a given image and save it into the target directory

        :param url: The url from which to fetch
        :type url: str
        :returns: The new name of the image
        """
        print('Trying to crawl image: {0}'.format(url));
        # prepare the initial request
        initial_request = Request(url, headers=self.req_headers);
        # try to fetch the page
        resp = request.urlopen(initial_request);
        # check if the server likes us
        if resp.status != 200:
            resp.close();
            raise RuntimeError('Server denied our connection with {0}: {1}'.format(resp.status, resp.reason));
        print('\tServer accepted our connection with {0}: {1}'.format(resp.status, resp.reason));
        # open the image to write to and write to it
        image_name = 'image' + str(self.image_index);
        image_file = open(self.target_directory + '/' + image_name, 'wb');
        image_file.write(resp.read());
        # close the response and the image file
        resp.close();
        image_file.close();
        # increment our image index
        self.image_index += 1;
        # return the name of the image
        return image_name

    def start_crawl(self):
        """Starts the crawl to download the story"""
        # load the chapter urls
        f = open(self.url_file);
        crawl_urls = f.readlines();
        f.close();
        # crawl the chapters
        for url in crawl_urls:
            self.fetch_content(url);

#parser = ShiroContentParser('shiro.txt', '/tmp/');
