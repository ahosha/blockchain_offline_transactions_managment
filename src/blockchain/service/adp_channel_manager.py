from src.common.settings import *
from src.blockchain.common.utils.utils_bc import *
from src.common.singleton_decorator import singleton
import traceback

@singleton
class ADPChannelManagerBC:
    adp_channel_manager = None
    adp_channel_manager_abi = None
    adp_manager_abi = None
    web3 = None
    pk_sender = None

    def __init__(self,
                 adp_channel_manager_address,
                 adp_channel_manager_abi,
                 web3):
        self.adp_channel_manager_address = adp_channel_manager_address
        self.adp_channel_manager_abi = adp_channel_manager_abi
        self.web3 = web3
        # print('on init channel manger -> adp_channel_manager_abi:{}'.format(self.adp_channel_manager_abi))

    def create_adp_channel_manager(self):
        self.adp_channel_manager = self.web3.eth.contract(
            address=self.web3.toChecksumAddress(ADPCHANNEL_MANAGER_ADDRESS),
            abi=self.adp_channel_manager_abi)

        return self.adp_channel_manager

    def get_channel_address_by_sender_address(self, token_address, address_sender):
        adp_channel_from_manager_trx = self.adp_channel_manager.functions.getChannel(
            self.web3.toChecksumAddress(token_address),
            address_sender)
        adp_channel_from_manager = adp_channel_from_manager_trx.call()
        return adp_channel_from_manager

    def create_adp_channel(self, token_address, address_sender=None):
        if not address_sender or FLASK_DEBUG:
            # address_sender = self.web3.personal.newAccount('the-passphrase')
            passphrase = 'KEYSMASH FJAFJKLDSKF7JKFDJ 1530'
            account = self.web3.eth.account.create('%s' % passphrase)
            address_sender = account.address
            self.pk_sender = self.web3.toHex(account.privateKey)
            # self.pk_sender = account.privateKey
        print('create_adp_channel token_address:{} address_sender:{}'.format(token_address, address_sender))
        self.token_address = token_address

        print(
            'createChannel buildTransaction parameters (token_address:{} address_sender:{} CLIENT_SYSTEM_ADDRESS:{} TRX_GRACETIME:{} )'.format(
                token_address,
                address_sender,
                CLIENT_SYSTEM_ADDRESS,
                TRX_GRACETIME))
        nonce = self.web3.eth.getTransactionCount(ITPS_SERVICE_ADDRESS)
        adpchannelmanager_txn = self.adp_channel_manager.functions.createChannel(
            self.web3.toChecksumAddress(token_address),
            address_sender,
            self.web3.toChecksumAddress(CLIENT_SYSTEM_ADDRESS),
            TRX_GRACETIME).buildTransaction({
            'gas': GAS_LIMIT_CHANNEL_CREATION,
            'gasPrice': GAS_PRICE,
            'nonce': nonce})
        print("build trx passed on adp channel manager. nonce:{}".format(nonce))
        BlockChainHelper().sign_send_trx(adpchannelmanager_txn)

        channel_address = self.get_channel_address_by_sender_address(token_address, address_sender)
        return channel_address, address_sender, self.pk_sender







