from src.common.singleton_decorator import singleton
import requests
import json
import sys, traceback
from src.common.settings import *


@singleton
class CallBackService:
    channel_state_url = "{}://{}:{}/{}".format(CLIENT_SYSTEM_BASE_PROTOCOL, CLIENT_SYSTEM_BASE_URL,
                                               CLIENT_SYSTEM_BASE_PORT, CLIENT_SYSTEM_CHANNEL_STATE_URL)

    def post_client_system_callback_channel_state(self,
                                                  event,
                                                  event_args_dict_json):
        try:
            if SEND_CALLBACK:
                final_url = self.channel_state_url

                payload = {}
                payload['event'] = event
                payload['event_args'] = event_args_dict_json

                # headers = {'Content-type': 'application/json'}

                headers = {'Content-type': 'application/json'}
                response = requests.post(final_url, data=json.dumps(payload), headers=headers)
                print(final_url)
                print(payload)
                print(response.text)  # TEXT/HTML
                print(response.status_code, response.reason)  # HTTP
        except Exception as expected:
            e = sys.exc_info()[0]
            print('CallBackService -> post_client_system_callback_channel_state Error: %s' % e)
            traceback.print_exc(file=sys.stdout)
            stacktrace = traceback.format_exc()

            exception = {
                'exception': expected,
                'stacktrace': stacktrace,
            }
            pass
