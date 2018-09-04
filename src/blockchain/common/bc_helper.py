from src.blockchain.service.rpc_provider import RPCProvider
from src.database.models.token_model import Token
import traceback
from src.common.settings import *

class BlockChainHelper:
    web3 = RPCProvider().create_rpc_provider()

    @classmethod
    def verify_signature_sha3(self, adp_channel, sha3_message, signature, signature_address):
        try:
            signature_v, signature_r, signature_s = self.parse_sign(signature)
            print('verify_signature_sha3->sha3_message:{} signature:{} v:{} r:{} s:{} '.format(sha3_message,
                                                                                    signature,
                                                                                    signature_v,
                                                                                    signature_r,
                                                                                    signature_s))
            verifed = adp_channel.channel_verify(sha3_message=sha3_message,
                                                 signature_v=signature_v,
                                                 signature_r=signature_r,
                                                 signature_s=signature_s,
                                                 address=signature_address)
            return verifed
        except:
            return False

    @classmethod
    def create_message_sha3(self, nonce, total_paid_to_receiver):
        return self.web3.soliditySha3(['uint256', 'uint256'], [nonce, total_paid_to_receiver])

    @classmethod
    def parse_sign(self, signature):
        if signature:
            v, r, s = signature[-1], signature[:32], signature[32:64]
            print('parse_sign->signature:{} v:{} r:{} s:{} '.format(signature,
                                                                    v,
                                                                    r,
                                                                    s))
            return v, r, s

    @classmethod
    def gen_signature(self, sha3_message, private_key):
        signed_message = self.web3.eth.account.signHash(sha3_message, private_key=private_key)
        # print('gen_signature->sha3_message:{} signature:{} v:{} r:{} s:{} messageHash:{}'.format(sha3_message,
        #                                                                                          signed_message.signature,
        #                                                                                          signed_message.v,
        #                                                                                          signed_message.r,
        #                                                                                          signed_message.s,
        #                                                                                          signed_message.messageHash))
        address = self.web3.eth.account.recoverHash(sha3_message, signature=signed_message.signature)

        print('gen_signature->sha3_message:{} signature:{} v:{} hex_r:{} hex_s:{} messageHash:{} address:{}'.format(
            sha3_message,
            signed_message.signature,
            signed_message.v,
            self.web3.toHex(
                signed_message.r),
            self.web3.toHex(
                signed_message.s),
            signed_message.messageHash,
            address))

        return signed_message.signature, signed_message.v, signed_message.r, signed_message.s, signed_message.messageHash

    @classmethod
    def hex_of_signature(self, byte_signature):
        return self.web3.toHex(byte_signature)

    @classmethod
    def bytes_of_signature(self, hex_signature):
        return self.web3.toBytes(hexstr=hex_signature)

    @classmethod
    def transfer_token_decimal_to_bc(self, token_address, amount):
        token = Token.find_by_token_address(token_address)
        token_multi = 10 ** token.token_decimal
        return int(amount * token_multi)

    @classmethod
    def transfer_token_decimal_from_bc(self, token_address, amount):
        token = Token.find_by_token_address(token_address)
        token_multi = 10 ** token.token_decimal
        return amount / token_multi

    @classmethod
    def prepare_sender_signature_sha3(self, sha3_message, pk_sender):
        signature, v, r, s, messageHash = self.gen_signature(sha3_message, pk_sender)
        return signature
        # signed_message = self.web3.eth.account.signHash(sha3_message, private_key=pk_sender)
        # print('prepare_sender_signature_sha3->signature:{} v:{} r:{} s:{} messageHash:{}'.format(signed_message.signature,
        #                                                                           signed_message.v,
        #                                                                           signed_message.r,
        #                                                                           signed_message.s,
        #                                                                           signed_message.messageHash))
        # return signed_message.signature

    @classmethod
    def prep_settlement(self, ccs, receiver_paid, sender_pk, receiver_pk):
        sha3_message = self.create_message_sha3(ccs, receiver_paid)
        receiver_signature, r_v, r_r, r_s, r_messageHash = self.gen_signature(sha3_message, receiver_pk)
        sender_signature, s_v, s_r, s_s, s_messageHash = self.gen_signature(sha3_message, sender_pk)

        # receiver_signature = self.web3.eth.account.signHash(sha3_message,
        #                                                     private_key=receiver_pk).signature
        # sender_signature = self.web3.eth.account.signHash(self.web3.toHex(sha3_message),
        #                                                   private_key=sender_pk).signature

        return sha3_message, receiver_signature, sender_signature

    @classmethod
    def sign_send_trx(self, trx):
        private_key = ITPS_SERVICE_PRIVATE_KEY
        self.web3.eth.enable_unaudited_features()
        signed_txn = self.web3.eth.account.signTransaction(trx, private_key=private_key)
        self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        trx_hash = signed_txn.hash
        tx_receipt = self.web3.eth.waitForTransactionReceipt(trx_hash)
        print('tx_receipt.status:{} (1-passed,0-failed)'.format(tx_receipt.status))
        if not tx_receipt.status:
            self.try_resend_trx(signed_txn, tx_receipt)

    @classmethod
    def try_resend_trx(self, signed_txn, tx_receipt):
        for i in range(TRX_FAILED_RETRY):
            try:
                self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
                tx_receipt = self.web3.eth.waitForTransactionReceipt(signed_txn.hash)
                if tx_receipt.status:
                    break
            except Exception as expected:
                if i == TRX_FAILED_RETRY - 1:
                    traceback.print_exc()
                    return None
        if not tx_receipt.status:
            print('Max retries exceeded with sendRawTransaction')