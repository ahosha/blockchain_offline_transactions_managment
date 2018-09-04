from src.common.settings import *
from src.common.singleton_decorator import singleton

@singleton
class EventMonitor:
    token_address = None
    token_abi = None
    adp_channel_manager_address = None
    adp_channel_manager_abi = None

    web3 = None

    def __init__(self, web3,
                 token_address,
                 token_abi,
                 adp_channel_manager_address,
                 adp_channel_manager_abi):
        self.web3 = web3
        self.token_address = token_address
        self.token_abi = token_abi
        self.adp_channel_manager_address = adp_channel_manager_address
        self.adp_channel_manager_abi = adp_channel_manager_abi


    def get_token_events(self, from_block):
        erc20 = self.web3.eth.contract(address=self.web3.toChecksumAddress(self.token_address),
                                       abi=self.token_abi)
        event_filter = erc20.eventFilter(TRANSFER_EVENT_NAME, {'fromBlock': from_block, 'toBlock': 'latest'})
        transfer_events = event_filter.get_all_entries()
        # check from args "to" to detect deposit with our channel_address  token_deposit
        # check from args "from" to detect withdraw with our channel_address  token_withdrawal
        return transfer_events


