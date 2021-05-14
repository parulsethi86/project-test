from html.parser import HTMLParser;
from os import path;
from urllib.parse import urlparse;
from urllib import request;
from urllib.request import Request;

class JaptemContentParser(HTMLParser):
    """Parses the content section of http://japtem.com/"""

    # headers to be used in a request
    req_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'
    };


    def __init__(self, url, target_directory, img_index = 1):
        # call the parent constructor
        super().__init__();
        # make sure we got a url
        if str(type(url)) != str(type('')):
            raise ValueError('url must be string');
        if len(url) == 0:
            raise ValueError('url must have a positive length');
        self.crawl_url = url;
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
        self.start_crawl();

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
        print('\tServer accepted our connection with {0}: {1}'.format(resp.status, resp.reason));
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

        # find the start of the content
        content_start = resp_body.find('<div class="post-content"');
        if content_start == -1:
            raise RuntimeError('Unable to find start of post-content');
        # find the previous|next chapter buttons
        next_chapter_point = resp_body.find('Next Chapter', content_start);
        if next_chapter_point == -1:
            raise RuntimeError('Unable to find link to next chapter');
        chapter_btn_start = resp_body.rfind('<h2', content_start, next_chapter_point);
        if chapter_btn_start == -1:
            raise RuntimeError('Unable to find start of chapter buttons');

        # get only the content
        post_content = resp_body[content_start:chapter_btn_start];
        # close the content div
        post_content += '</div>';
        # feed the content to the parser
        self.feed(post_content);

        # check if there is another chapter after this
        divider_pos = resp_body.find('|', chapter_btn_start);
        if divider_pos == -1:
            raise RuntimeError('Unable to find divider of chapter buttons');
        pos_link_next_chapter = resp_body.find('<a', divider_pos);
        if pos_link_next_chapter != -1:
            # scan to href
            next_href_pos = resp_body.find('href=', pos_link_next_chapter);
            if next_href_pos == -1:
                raise RuntimeError('Link to next chapter is missing href');
            # adjust to start of string
            next_href_pos += 6;
            # check for closing "
            closing_quote_pos = resp_body.find('"', next_href_pos);
            if next_href_pos == -1:
                raise RuntimeError('Link href to next chapter is missing closing "');
            # get url to next chapter and return it
            url_to_next_chapter = resp_body[next_href_pos:closing_quote_pos];
            return url_to_next_chapter;
        # no other chapter
        return "";

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
        # perform the first crawl
        next_chapter_url = self.fetch_content(self.crawl_url);
        # extend the next chapter url
        next_chapter_url = self.complete_url(next_chapter_url);
        # continue crawling until there is no next chapter
        while len(next_chapter_url) > 0:
            next_chapter_url = self.fetch_content(next_chapter_url);
            next_chapter_url = self.complete_url(next_chapter_url);

#f = open('sample3.html', 'r');
#post_content = f.read();
#f.close();
parser = JaptemContentParser('http://japtem.com/dd-volume-1-chapter-1/', '/tmp/');
#parser.feed(post_content);
