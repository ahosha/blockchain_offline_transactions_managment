from src.common.singleton_decorator import singleton
from web3 import Web3, HTTPProvider
from src.common.settings import *
from src.blockchain.common.utils.utils_json import Utils

# from web3.middleware import geth_poa_middleware
from web3.middleware import (
    construct_fixture_middleware,
    geth_poa_middleware,
)


@singleton
class RPCProvider:
    web3 = None

    def __init__(self):
        """ create web3 client """
        # Note that you should create only one RPCProvider per
        # process, as it recycles underlying TCP/IP network connections between
        # your process and Ethereum node
        if not USE_INFURA:
            endpoint_uri = '{}://{}:{}'.format(NODE_PROTOCOL, NODE_HOST, NODE_PORT)
        else:
            endpoint_uri = '{}://{}'.format(INFURA_PROTOCOL, INFURA_NODE_HOST)
        print('web3 endpoint_uri:{}'.format(endpoint_uri))
        self.web3 = Web3(HTTPProvider(endpoint_uri))
        print('web3 endpoint_uri:{} done'.format(endpoint_uri))
        # self.web3 = Web3(HTTPProvider('{}://{}'.format(NODE_PROTOCOL, NODE_HOST)))

        self.web3.middleware_stack.inject(geth_poa_middleware, layer=0)
        print('web3 endpoint_uri:{} middleware_stack.inject'.format(endpoint_uri))
        latest_block = self.web3.eth.getBlock('latest')
        print("*************latest block:{}********************".format(latest_block))

        # import os
        # my_path = os.path.abspath(os.path.dirname(__file__))
        # channel_manager_abi_path = os.path.join(my_path,
        #                                         "../common/ABI/{}".format("ADPChannelManager.json"))
        # channel_manager_abi = Utils.read_json(channel_manager_abi_path)
        #
        # channel_manager = self.web3.eth.contract(
        #     address=self.web3.toChecksumAddress(ADPCHANNEL_MANAGER_ADDRESS),
        #     abi=channel_manager_abi["abi"])

        # adpchannelmanager_txn = channel_manager.functions.createChannel(
        #     self.web3.toChecksumAddress('0x102199295fc31f2298a05136affcad9d68233ead'),
        #     '0x00977d743b1db725F4e392554824786f944c2e89',
        #     self.web3.toChecksumAddress('0x6C9EcaD3fF968Fc533f44AeCeC19eBF8FA628c24'),
        #     0).buildTransaction({
        #     'gas': GAS_LIMIT_CHANNEL_CREATION,
        #     'gasPrice': GAS_PRICE,
        #     'nonce': 68})

        # print("build trx passed. channel_manager_abi:{}".format(channel_manager_abi["abi"]))
        # private_key = ITPS_SERVICE_PRIVATE_KEY
        # self.web3.eth.enable_unaudited_features()
        # signed_txn = self.web3.eth.account.signTransaction(adpchannelmanager_txn, private_key=private_key)
        # self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        # trx_hash = signed_txn.hash
        # tx_receipt = self.web3.eth.waitForTransactionReceipt(trx_hash)
        # print('tx_receipt:{}'.format(tx_receipt.status))
        # # 	createChannel buildTransaction parameters (
        # # 	token_address:0x102199295fc31f2298a05136affcad9d68233ead
        # # 	address_sender:0x00977d743b1db725F4e392554824786f944c2e89
        # # 	CLIENT_SYSTEM_ADDRESS:0x6C9EcaD3fF968Fc533f44AeCeC19eBF8FA628c24
        # # 	TRX_GRACETIME:0 )
        # channel_address = self.get_channel_address_by_sender_address('0x102199295fc31f2298a05136affcad9d68233ead ',
        #                                                              '0x00977d743b1db725F4e392554824786f944c2e89')
        # print('channel address: {}', channel_address)

    def create_rpc_provider(self):
        """ create web3 client """
        # Note that you should create only one RPCProvider per
        # process, as it recycles underlying TCP/IP network connections between
        # your process and Ethereum node
        return self.web3
