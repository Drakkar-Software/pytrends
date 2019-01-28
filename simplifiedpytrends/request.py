from __future__ import absolute_import, print_function, unicode_literals

import json

import requests

from simplifiedpytrends import exceptions


class TrendReq(object):
    """
    Google Trends API
    """

    GET_METHOD = 'get'
    POST_METHOD = 'post'

    GENERAL_URL = 'https://trends.google.com/trends/api/explore'
    INTEREST_OVER_TIME_URL = 'https://trends.google.com/trends/api/widgetdata/multiline'
    INTEREST_BY_REGION_URL = 'https://trends.google.com/trends/api/widgetdata/comparedgeo'
    RELATED_QUERIES_URL = 'https://trends.google.com/trends/api/widgetdata/relatedsearches'
    TRENDING_SEARCHES_URL = 'https://trends.google.com/trends/hottrends/hotItems'
    TOP_CHARTS_URL = 'https://trends.google.com/trends/topcharts/chart'
    SUGGESTIONS_URL = 'https://trends.google.com/trends/api/autocomplete/'
    CATEGORIES_URL = 'https://trends.google.com/trends/api/explore/pickers/category'

    def __init__(self, hl='en-US', tz=360, geo='', proxies=''):
        """
        Initialize default values for params
        """
        # google rate limit
        self.google_rl = 'You have reached your quota limit. Please try again later.'
        self.results = None

        # set user defined options used globally
        self.tz = tz
        self.hl = hl
        self.geo = geo
        self.kw_list = list()
        self.proxies = proxies #add a proxy option
        self.cookies = dict(filter(
            lambda i: i[0] == 'NID',
            requests.get(
                'https://trends.google.com/?geo={geo}'.format(geo=hl[-2:])
            ).cookies.items()
        ))

        # intialize widget payloads
        self.token_payload = dict()
        self.interest_over_time_widget = dict()
        self.interest_by_region_widget = dict()
        self.related_topics_widget_list = list()
        self.related_queries_widget_list = list()

    def _get_data(self, url, method=GET_METHOD, trim_chars=0, **kwargs):
        """Send a request to Google and return the JSON response as a Python object

        :param url: the url to which the request will be sent
        :param method: the HTTP method ('get' or 'post')
        :param trim_chars: how many characters should be trimmed off the beginning of the content of the response
            before this is passed to the JSON parser
        :param kwargs: any extra key arguments passed to the request builder (usually query parameters or data)
        :return:
        """
        s = requests.session()
        s.headers.update({'accept-language': self.hl})
        if self.proxies != '':
            s.proxies.update(self.proxies)
        if method == TrendReq.POST_METHOD:
            response = s.post(url, cookies=self.cookies, **kwargs)
        else:
            response = s.get(url, cookies=self.cookies, **kwargs)

        # check if the response contains json and throw an exception otherwise
        # Google mostly sends 'application/json' in the Content-Type header,
        # but occasionally it sends 'application/javascript
        # and sometimes even 'text/javascript
        if 'application/json' in response.headers['Content-Type'] or \
            'application/javascript' in response.headers['Content-Type'] or \
                'text/javascript' in response.headers['Content-Type']:

            # trim initial characters
            # some responses start with garbage characters, like ")]}',"
            # these have to be cleaned before being passed to the json parser
            content = response.text[trim_chars:]

            # parse json
            return json.loads(content)
        else:
            # this is often the case when the amount of keywords in the payload for the IP
            # is not allowed by Google
            raise exceptions.ResponseError('The request failed: Google returned a '
                                           'response with code {0}.'.format(response.status_code), response=response)

    def build_payload(self, kw_list, cat=0, timeframe='today 5-y', geo='', gprop=''):
        """Create the payload for related queries, interest over time and interest by region"""
        self.kw_list = kw_list
        self.geo = geo
        self.token_payload = {
            'hl': self.hl,
            'tz': self.tz,
            'req': {'comparisonItem': [], 'category': cat, 'property': gprop}
        }

        # build out json for each keyword
        for kw in self.kw_list:
            keyword_payload = {'keyword': kw, 'time': timeframe, 'geo': self.geo}
            self.token_payload['req']['comparisonItem'].append(keyword_payload)
        # requests will mangle this if it is not a string
        self.token_payload['req'] = json.dumps(self.token_payload['req'])
        # get tokens
        self._tokens()
        return

    def _tokens(self):
        """Makes request to Google to get API tokens for interest over time, interest by region and related queries"""

        # make the request and parse the returned json
        widget_dict = self._get_data(
            url=TrendReq.GENERAL_URL,
            method=TrendReq.GET_METHOD,
            params=self.token_payload,
            trim_chars=4,
        )['widgets']

        # order of the json matters...
        first_region_token = True
        # clear self.related_queries_widget_list and self.related_topics_widget_list
        # of old keywords'widgets
        self.related_queries_widget_list[:] = []
        self.related_topics_widget_list[:] = []
        # assign requests
        for widget in widget_dict:
            if widget['id'] == 'TIMESERIES':
                self.interest_over_time_widget = widget
            if widget['id'] == 'GEO_MAP' and first_region_token:
                self.interest_by_region_widget = widget
                first_region_token = False
            # response for each term, put into a list
            if 'RELATED_TOPICS' in widget['id']:
                self.related_topics_widget_list.append(widget)
            if 'RELATED_QUERIES' in widget['id']:
                self.related_queries_widget_list.append(widget)
        return

    # returns a list of dicts containing {"timestamp", "data"}
    def interest_over_time(self):
        """Request data from Google's Interest Over Time section and return a dataframe"""

        over_time_payload = {
            # convert to string as requests will mangle
            'req': json.dumps(self.interest_over_time_widget['request']),
            'token': self.interest_over_time_widget['token'],
            'tz': self.tz
        }

        # make the request and parse the returned json
        req_json = self._get_data(
            url=TrendReq.INTEREST_OVER_TIME_URL,
            method=TrendReq.GET_METHOD,
            trim_chars=5,
            params=over_time_payload,
        )

        result_list = []
        timestamp_key = "timestamp"
        data_key = "data"

        for req_data in req_json['default']['timelineData']:
            result_list.append({
                timestamp_key: float(req_data["time"]),
                data_key: float(req_data["value"][0])
            })

        # sort by time
        sorted_result = sorted(result_list, key=lambda a: a[timestamp_key])

        return sorted_result
