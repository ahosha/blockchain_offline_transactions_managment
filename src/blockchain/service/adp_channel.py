from src.common.settings import *
from src.common.singleton_decorator import singleton
from src.blockchain.common.bc_helper import BlockChainHelper


@singleton
class ADPChannelBC:
    adp_channel_manager = None
    channel_address = None
    channel_abi = None
    address_sender = None

    adp_channel_address_from_manager = None
    adp_channel_contract = None
    web3 = None

    def __init__(self, adp_channel_manager,
                 channel_address,
                 channel_abi,
                 web3,
                 address_sender=None):

        self.adp_channel_manager = adp_channel_manager
        self.channel_address = channel_address
        self.channel_abi = channel_abi
        self.address_sender = address_sender
        self.web3 = web3

    def get_channel_address_by_address_from_channel_manager(self):
        if not self.adp_channel_address_from_manager:
            adp_channel_from_manager_trx = self.adp_channel_manager.functions.getChannel(
                self.web3.toChecksumAddress(self.channel_address),
                self.address_sender)
            self.adp_channel_address_from_manager = adp_channel_from_manager_trx.call()
        return self.adp_channel_address_from_manager

    def create_adp_channel_contract(self):
        if self.channel_address == EMPTY_CHANNEL:
            self.channel_address = self.get_channel_address_by_address_from_channel_manager()
        if self.channel_address != EMPTY_CHANNEL:
            if not self.adp_channel_contract:
                self.adp_channel_contract = self.web3.eth.contract(address=self.channel_address,
                                                                   abi=self.channel_abi)
            return self.adp_channel_contract

    def adp_channel_contract_exists(self):
        if not self.adp_channel_contract:
            self.create_adp_channel_contract()
        return True

    def withdraw(self):
        if self.adp_channel_contract_exists():
            nonce = self.web3.eth.getTransactionCount(ITPS_SERVICE_ADDRESS)
            adpchannel_txn = self.adp_channel_contract.functions.withdrawal().buildTransaction({
                'gas': GAS_LIMIT_WITHDRAW,
                'gasPrice': GAS_PRICE,
                'nonce': nonce})
            BlockChainHelper().sign_send_trx(adpchannel_txn)
            return

    def settlement(self,
                   ccs_nonce,
                   total_paid_to_receiver,
                   receiver_signature,
                   sender_signature,
                   sender_key,
                   token_address,
                   withdrawal_amount=None):
        if self.adp_channel_contract_exists():
            total_paid_to_receiver_for_sign = BlockChainHelper().transfer_token_decimal_to_bc(
                token_address,
                total_paid_to_receiver)
            sha3_message = BlockChainHelper().create_message_sha3(ccs_nonce, total_paid_to_receiver_for_sign)
            # b_sender_signature = BlockChainHelper().bytes_of_signature(sender_signature)
            sender_signature_verified = BlockChainHelper().verify_signature_sha3(self,
                                                                                 sha3_message,
                                                                                 sender_signature,
                                                                                 self.address_sender)
            print(
                'api settlement sender_signature_verified:{} sha3_message:{} receiver_signature:{}'.format(
                    sender_signature_verified,
                    sha3_message,
                    receiver_signature))

            # b_receiver_signature = BlockChainHelper().bytes_of_signature(receiver_signature)
            receiver_signature_verified = BlockChainHelper().verify_signature_sha3(self,
                                                                                   sha3_message,
                                                                                   receiver_signature,
                                                                                   ITPS_SERVICE_ADDRESS)
            print(
                'api settlement receiver_signature_verified:{} sha3_message:{} receiver_signature:{}'.format(
                    receiver_signature_verified,
                    sha3_message,
                    receiver_signature))

            if sender_signature_verified and receiver_signature_verified:
                receiver_v, receiver_r, receiver_s = BlockChainHelper().parse_sign(receiver_signature)
                sender_v, sender_r, sender_s = BlockChainHelper().parse_sign(sender_signature)
                if withdrawal_amount and withdrawal_amount != 0:
                    trx_name = 'settlementSender'
                    settlement_txn = self.adp_channel_contract.functions.settlementSender(ccs_nonce,
                                                                                          total_paid_to_receiver_for_sign,
                                                                                          withdrawal_amount,
                                                                                          self.web3.toInt(receiver_v),
                                                                                          self.web3.toHex(receiver_r),
                                                                                          self.web3.toHex(receiver_s),
                                                                                          self.web3.toInt(sender_v),
                                                                                          self.web3.toHex(sender_r),
                                                                                          self.web3.toHex(sender_s))
                else:
                    trx_name = 'settlementReceiver'
                    settlement_txn = self.adp_channel_contract.functions.settlementReceiver(ccs_nonce,
                                                                                            total_paid_to_receiver_for_sign,
                                                                                            self.web3.toInt(receiver_v),
                                                                                            self.web3.toHex(receiver_r),
                                                                                            self.web3.toHex(receiver_s),
                                                                                            self.web3.toInt(sender_v),
                                                                                            self.web3.toHex(sender_r),
                                                                                            self.web3.toHex(sender_s)
                                                                                            )
                nonce_to_trx = self.web3.eth.getTransactionCount(ITPS_SERVICE_ADDRESS)
                txn_build_transaction = settlement_txn.buildTransaction(
                    {'gas': GAS_LIMIT_SETTLEMENT, 'gasPrice': GAS_PRICE, 'nonce': nonce_to_trx})
                print("build trx passed on adp channel -> txn_build_transaction. nonce_to_trx:{}".format(nonce_to_trx))
                BlockChainHelper().sign_send_trx(txn_build_transaction)
                channel_current_state = self.adp_channel_contract.functions.getChannel().call()
                return channel_current_state
            else:
                print('wrong signatures: sender_signature_verified:{} receiver_signature_verified:{} '.format(
                    sender_signature_verified, receiver_signature_verified))
                return None
        else:
            return None

    def get_channel(self):
        if self.adp_channel_contract_exists():
            """
              0  uint balance, //Amount of tokens on the account of a Channel Contract
              1  uint capacity,
              2  uint senderWithdrawableAmount,
              3  uint receiverWithdrawableAmount,
              4  uint nonce,
              5  uint cumulativeAmountWithdrawedByReceiver,
              6  ContractStatus status
            """
            return self.adp_channel_contract.functions.getChannel().call()
        else:
            return None

    def get_channel_status(self):
        return self.get_channel(self.web3)[6]

    def channel_verify(self, sha3_message, signature_v, signature_r, signature_s, address):
        if self.adp_channel_contract_exists():
            v = self.web3.toInt(signature_v)
            r = self.web3.toHex(signature_r)
            s = self.web3.toHex(signature_s)
            print('channel_verify->sha3_message:{} v:{} hex_r:{} hex_s:{} address:{}'.format(sha3_message, v, r, s,
                                                                                             address))
            return self.adp_channel_contract.functions.verify(sha3_message,
                                                              self.web3.toInt(signature_v),
                                                              self.web3.toHex(signature_r),
                                                              self.web3.toHex(signature_s),
                                                              address
                                                              ).call()
        else:
            return False
