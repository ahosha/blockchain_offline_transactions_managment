from rx import Observable, Observer
from src.state.serverstate import ServerState
from src.common.singleton_decorator import singleton
from src.common.consts import DB_MONITOR_SUB, BC_MONITOR_SUB


@singleton
class CallBackService:
    callback_db_data = None

    def __init__(self):
        # ServerState().select(observer_name=DB_MONITOR_SUB).subscribe(
        #     on_next=lambda value: print("Received {0}".format(value)),
        #     on_completed=lambda: print("Done!"),
        #     on_error=lambda error: print("Error Occurred: {0}".format(error))
        # )
        ServerState().select(observer_name=DB_MONITOR_SUB).subscribe(DBCallBackService())

    def db_callback_onnext(self, data):
        self.callback_db_data = data
        return


class DBCallBackService(Observer):

    def on_next(self, value):
        # call client system
        print("1 Received {0}".format(value))
        self.post_client_system_callback_channel_state(value)

    def on_completed(self):
        print("1 Done!")

    def on_error(self, error):
        print("1 Error Occurred: {0}".format(error))

    def post_client_system_callback_channel_state(self, input_data):

        import requests
        import json
        # data = json.loads(input_data)
        base_url = "127.0.0.1:5001"
        final_url = "http://{0}/{1}".format(base_url, 'api/channelstate/')
        payload = {"event": "string",
                   "Channel Snapshot ": {
                       "ext_account_id": "string",
                       "user_public_key": "string",
                       "channel_balance": 0,
                       "channel_capacity": 0,
                       "channel_status": "string",
                       "last_settled_nonce": 0,
                       "available_for_settlement_to_sender": 0,
                       "available_for_settlement_to_receiver": 0
                   }
                   }
        headers = {'Content-type': 'application/json'}
        response = requests.post(final_url, data=payload, headers=headers)
        print(final_url)
        print(payload)
        print(response.text)  # TEXT/HTML
        print(response.status_code, response.reason)  # HTTP
