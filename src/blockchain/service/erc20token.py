from src.common.settings import *
from src.blockchain.common.utils.utils_bc import *
from src.common.singleton_decorator import singleton
import traceback


@singleton
class ERC20Token:
    token_address = None
    token_abi = None
    address_sender = None
    web3 = None

    def __init__(self, token_address,
                 token_abi,
                 web3,
                 address_sender=None):
        self.token_address = token_address
        self.token_abi = token_abi
        self.address_sender = address_sender
        self.web3 = web3

    def transfer(self, transfer_amount, channel_address):
        # transfer to channel

        erc20 = self.web3.eth.contract(address=self.web3.toChecksumAddress(self.token_address),
                                       abi=self.token_abi)
        nonce = self.web3.eth.getTransactionCount(ITPS_SERVICE_ADDRESS)
        transfer_txn = erc20.functions.transfer(self.web3.toChecksumAddress(channel_address),
                                                transfer_amount).buildTransaction({
            'gas': GAS_LIMIT_TRANSFER,
            'gasPrice': GAS_PRICE,
            'nonce': nonce})
        BlockChainHelper().sign_send_trx(transfer_txn)
        return

    def get_decimal(self):
        # create contract on input_token_address, get decimal ,save

        erc20token = self.web3.eth.contract(address=self.web3.toChecksumAddress(self.token_address),
                                            abi=self.token_abi)
        if erc20token:
            return erc20token.functions.decimals().call()
        else:
            return None
