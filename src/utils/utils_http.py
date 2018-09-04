import requests
import sys
import json

class HTTPHelper:

    @classmethod
    def post_to_url(self, payload, final_url, params=None):
        try:
            headers = {'Content-type': 'application/json'}
            if not params:
                response = requests.post(final_url, data=json.dumps(payload), headers=headers)
            else:
                requests.post(final_url, params=params, data=json.dumps(payload), headers=headers)
            print(final_url)
            print(payload)
            print(response.text)  # TEXT/HTML
            print(response.status_code, response.reason)  # HTTP
            return response.text, response.status_code, response.reason
        except Exception as expected:
            e = sys.exc_info()[0]
            print('post_to_url Error: %s' % e)
            pass

    @classmethod
    def get_from_url(payload, final_url):
        try:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate'}
            response = requests.get(url=final_url, params=payload, headers=headers)
            print(response.url)
            print(response.text)  # TEXT/HTML
            print(response.status_code, response.reason)  # HTTP
            return response.text, response.status_code, response.reason
        except Exception as expected:
            e = sys.exc_info()[0]
            print('post_to_url Error: %s' % e)
            pass
