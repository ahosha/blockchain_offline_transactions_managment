from src.common.settings import *
from src.blockchain.service.rpc_provider import RPCProvider

from src.blockchain.service.adp_channel import ADPChannelBC
from src.blockchain.service.adp_channel_manager import ADPChannelManagerBC
from src.common.singleton_decorator import singleton
from src.blockchain.service.erc20token import ERC20Token
from src.blockchain.service.event_monitor import EventMonitor
from src.common.bc_commands import BCCommands, BCCommandsStatus
from sqlalchemy.orm.attributes import flag_modified
from src.blockchain.common.bc_helper import BlockChainHelper
from src.callback.call_back_service import CallBackService

from src.business.account import *
from src.business.channel import *
from src.business.token import *
from src.blockchain.common.utils.utils_bc import *


@singleton
class BlockChainService:
    token_abi = None
    adp_channel_manager_address = None
    adp_channel_manager_abi = None
    adp_channel_abi = None

    adp_channel_manager = None
    adp_channel = None
    erc20_token = None
    event_monitor = None

    web3 = None

    def __init__(self, token_abi,
                 adp_channel_manager_address, adp_channel_manager_abi,
                 adp_channel_abi):
        self.token_abi = token_abi
        self.adp_channel_manager_address = adp_channel_manager_address
        self.adp_channel_manager_abi = adp_channel_manager_abi
        self.adp_channel_abi = adp_channel_abi
        self.setup()
        # print('BlockChainService.init->token_abi:{}'.format(token_abi))
        # print('BlockChainService.init->channel_manager_abi:{}'.format(adp_channel_manager_abi))
        # print('BlockChainService.init->channel_abi:{}'.format(adp_channel_abi))

    def setup(self):
        self.web3 = RPCProvider().create_rpc_provider()

    def get_latest_block_number(self):
        return self.web3.eth.getBlock('latest').number

    def get_channel_manager_events(self, from_block):
        # print(
        #     'BlockChainService.get_channel_manager_events->channel_manager_abi:{}'.format(self.adp_channel_manager_abi))
        adp_channel_manager_contract = self.web3.eth.contract(
            address=self.web3.toChecksumAddress(self.adp_channel_manager_address),
            abi=self.adp_channel_manager_abi)
        event_filter = adp_channel_manager_contract.eventFilter(SETTLEMENT_EVENT_NAME,
                                                                {'fromBlock': from_block,
                                                                 'toBlock': 'latest'}
                                                                )
        return event_filter.get_all_entries()

    def create_adp_channel_manager(self):
        # print(
        #     'BlockChainService.create_adp_channel_manager->channel_manager_abi:{}'.format(self.adp_channel_manager_abi))
        self.adp_channel_manager = ADPChannelManagerBC(adp_channel_manager_address=self.adp_channel_manager_address,
                                                       adp_channel_manager_abi=self.adp_channel_manager_abi,
                                                       web3=self.web3)
        self.adp_channel_manager.create_adp_channel_manager()

    def create_erc20_token(self, token_address):
        self.erc20_token = ERC20Token(token_address=token_address,
                                      token_abi=self.token_abi,
                                      web3=self.web3)
        self.erc20_token

    def create_event_monitor(self, token_address):
        self.event_monitor = EventMonitor(web3=self.web3,
                                          token_address=token_address,
                                          token_abi=self.token_abi,
                                          adp_channel_manager_address=self.adp_channel_manager_address,
                                          adp_channel_manager_abi=self.adp_channel_manager_abi)
        return self.event_monitor

    def adp_channel_manager_exists(self):
        if not self.adp_channel_manager:
            self.create_adp_channel_manager()
        return self.adp_channel_manager

    def create_adp_channel_contract(self, token_address, address_sender, channel_address):
        if self.adp_channel_manager_exists():
            if not channel_address:
                channel_address = self.adp_channel_manager.get_channel_address_by_sender_address(token_address,
                                                                                                 address_sender)
            if channel_address != EMPTY_CHANNEL:
                self.adp_channel = ADPChannelBC(adp_channel_manager=self.adp_channel_manager,
                                                channel_address=channel_address,
                                                channel_abi=self.adp_channel_abi,
                                                web3=self.web3,
                                                address_sender=address_sender)
                self.adp_channel.create_adp_channel_contract()
            return

    def get_adp_channel_bc_by_channel_address(self, channel_address, address_sender):
        if self.adp_channel_manager_exists():
            if channel_address != EMPTY_CHANNEL:
                self.adp_channel = ADPChannelBC(adp_channel_manager=self.adp_channel_manager,
                                                channel_address=channel_address,
                                                channel_abi=self.adp_channel_abi,
                                                web3=self.web3,
                                                address_sender=address_sender)
                return self.adp_channel.get_channel()
            return

    def get_adp_channel_manager(self):
        if not self.adp_channel_manager:
            self.create_adp_channel_manager()
        return self.adp_channel_manager

    def get_adp_channel(self, token_address, address_sender, channel_address):
        if not self.adp_channel:
            self.create_adp_channel_contract(token_address, address_sender, channel_address)
        return self.adp_channel

    def get_erc20_token(self, token_address):
        if not self.erc20_token:
            self.create_erc20_token(token_address)
        return self.erc20_token

    def get_erc20_token_by_address(self, token_address, token_abi):
        return ERC20Token(token_address=token_address,
                          token_abi=token_abi,
                          web3=self.web3)

    # __________________________________________________________

    def perform_commands(self, commands_to_do):
        # check sequence
        for command in commands_to_do:
            print('>>>>> block chain service perform_commands {} <<<<<'.format(command.command_name))
            self.update_inprocess_command(command)
            if command.command_name == BCCommands.CREATE_CHANNEL.name:
                self.handle_create_channel(command)
            # elif command.command_name == BCCommands.TRANSFER.name:
            #     # do TRANSFER
            elif command.command_name == BCCommands.GET_DECIMAL.name:
                self.handle_get_decimal(command)
            elif command.command_name == BCCommands.SETTLEMENT.name:
                self.handle_settlement(command)
            elif command.command_name == BCCommands.WITHDRAW.name:
                self.handle_withdraw(command)
            # elif command.command_name == BCCommands.SYNC_CHANNEL.name:
            #     # do SYNC_CHANNEL

    def handle_create_channel(self, command):
        external_account_id = command.command_args['external_account_id']
        token_address = command.command_args['input_token_address']
        external_account = Account.find_by_ext_account_id(external_account_id)
        user_public_account = Account.find_by_user_public_key(command.user_public_key)
        if external_account or user_public_account:
            self.update_failed_command(command)
            print("external_account_id or user_public_key already exists")
            return
        adp_channel_manager = self.get_adp_channel_manager()
        user_public_key = command.user_public_key
        token_decimal = self.get_token_decimal_from_contract(token_address)
        print('>>>>> handle_create_channel token_address:{} user_public_key:{} <<<<<'.format(token_address,
                                                                                             user_public_key))
        channel_address, user_public_key, pk_sender = adp_channel_manager.create_adp_channel(token_address,
                                                                                             user_public_key)

        if FLASK_DEBUG:
            erc20_token = self.get_erc20_token(token_address)
            erc20_token.transfer(transfer_amount=TRANSFER_AMOUNT, channel_address=channel_address)
        print('>>>>> create_account_channel_on_db')
        # save account to DB
        sender_address = create_account_channel_on_db(channel_address, external_account_id,
                                                      token_address, pk_sender,
                                                      user_public_key,
                                                      token_decimal)
        print('>>>>> call_create_channel_callback')
        # call client system callback service
        self.call_create_channel_callback(channel_address, external_account_id, sender_address)

        adp_channel_manager = self.get_adp_channel_manager()
        adp_channel = self.get_adp_channel(token_address=token_address,
                                           address_sender=user_public_key,
                                           channel_address=channel_address)
        print('>>>>> get_adp_channel done')
        if adp_channel:
            adp_channel_from_bc = adp_channel.get_channel()
            channel_from_db = Channel.find_by_channel_address(adp_channel.channel_address)
            if channel_from_db:
                update_channel_on_db(channel_from_db=channel_from_db,
                                     adp_channel_from_bc=adp_channel_from_bc,
                                     token_address=token_address)
                self.update_command_on_db(command)
            else:
                self.update_failed_command(command)
        else:
            self.update_failed_command(command)
        return

    def call_create_channel_callback(self, channel_address, external_account_id, sender_addres):
        event_args = {}
        event_args['user_public_key'] = sender_addres
        event_args['ext_account_id'] = external_account_id
        event_args['channel_address'] = channel_address
        CallBackService().post_client_system_callback_channel_state(event="channel_created",
                                                                    event_args_dict_json=event_args)

    def handle_get_decimal(self, command):
        token_address = command.command_args['token_address']
        self.save_token_to_db(token_address)
        self.update_command_on_db(command)

    def save_token_to_db(self, token_address):
        token_decimal = self.get_token_decimal_from_contract(token_address)
        create_token(token_address, token_decimal)

    def get_token_decimal_from_contract(self, token_address):
        erc20_token = self.get_erc20_token_by_address(token_address, self.token_abi)
        return erc20_token.get_decimal()

    def handle_withdraw(self, command):
        adp_channel_manager = self.get_adp_channel_manager()
        token_address = command.command_args['token_address']
        channel_address = adp_channel_manager.get_channel_address_by_sender_address(
            token_address=token_address,
            address_sender=command.user_public_key)
        adp_channel = self.get_adp_channel(token_address=token_address,
                                           address_sender=command.user_public_key,
                                           channel_address=channel_address)
        if adp_channel:
            adp_channel.withdraw()
            adp_channel_from_bc = adp_channel.get_channel()
            channel_from_db = Channel.find_by_channel_address(adp_channel.channel_address)
            if channel_from_db:
                update_channel_on_db(channel_from_db=channel_from_db,
                                     adp_channel_from_bc=adp_channel_from_bc,
                                     token_address=token_address)
                self.update_command_on_db(command)
            else:
                self.update_failed_command(command)
        else:
            self.update_failed_command(command)

    def handle_settlement(self, command):
        adp_channel_manager = self.get_adp_channel_manager()
        token_address = command.command_args['token_address']
        channel_address = adp_channel_manager.get_channel_address_by_sender_address(
            token_address=token_address,
            address_sender=command.user_public_key)
        adp_channel = self.get_adp_channel(token_address=token_address,
                                           address_sender=command.user_public_key,
                                           channel_address=channel_address)
        if adp_channel:
            nonce = command.command_args['ccs_nonce']

            total_paid_to_receiver = command.command_args['total_paid_to_receiver']
            receiver_signature = BlockChainHelper().bytes_of_signature(command.command_args['receiver_signature'])
            sender_signature = BlockChainHelper().bytes_of_signature(command.command_args['sender_signature'])
            withdrawal_amount = command.command_args['withdrawal_amount']
            total_paid_to_receiver_for_sign = BlockChainHelper().transfer_token_decimal_to_bc(token_address,
                                                                                              total_paid_to_receiver)
            sha3_message = BlockChainHelper().create_message_sha3(nonce, total_paid_to_receiver_for_sign)
            sender_signature_verified = BlockChainHelper().verify_signature_sha3(adp_channel,
                                                                                 sha3_message,
                                                                                 sender_signature,
                                                                                 command.user_public_key)
            print('bis settlement sender_signature_verified:{} sha3_message:{} sender_signature:{}'.format(
                sender_signature_verified,
                sha3_message,
                sender_signature))

            receiver_signature_verified = BlockChainHelper().verify_signature_sha3(adp_channel,
                                                                                   sha3_message,
                                                                                   receiver_signature,
                                                                                   ITPS_SERVICE_ADDRESS)
            print('bis settlement receiver_signature_verified:{} sha3_message:{} receiver_signature:{}'.format(
                receiver_signature_verified,
                sha3_message,
                receiver_signature))

            if receiver_signature_verified and sender_signature_verified:
                adp_channel_from_bc = adp_channel.get_channel()
                print(
                    "send settlement ccs_nonce={} total_paid_to_receiver={} receiver_signature={} sender_signature={}  withdrawal_amount={} sender_key={} ".format(
                        nonce,
                        total_paid_to_receiver,
                        receiver_signature,
                        sender_signature, withdrawal_amount, command.user_public_key))
                channel_current_state = adp_channel.settlement(ccs_nonce=nonce,
                                                               total_paid_to_receiver=total_paid_to_receiver,
                                                               receiver_signature=receiver_signature,
                                                               sender_signature=sender_signature,
                                                               withdrawal_amount=withdrawal_amount,
                                                               sender_key=command.user_public_key,
                                                               token_address=token_address
                                                               )
                if not channel_current_state:
                    print('settlement on block chain failed')
                    self.update_failed_command(command)
                else:
                    adp_channel_from_bc = adp_channel.get_channel()
                    channel_from_db = Channel.find_by_channel_address(adp_channel.channel_address)
                    if channel_from_db:
                        update_channel_on_db(channel_from_db=channel_from_db,
                                             adp_channel_from_bc=adp_channel_from_bc,
                                             token_address=token_address)
                        self.update_command_on_db(command)
                    else:
                        self.update_failed_command(command)
                    print(
                        "settlement done -> channel balance:{} capacity:{} senderWithdrawableAmount:{} receiverWithdrawableAmount:{} nonce:{} cumulativeAmountWithdrawedByReceiver:{}".format(
                            adp_channel_from_bc[0],
                            adp_channel_from_bc[1],
                            adp_channel_from_bc[2],
                            adp_channel_from_bc[3],
                            adp_channel_from_bc[4],
                            adp_channel_from_bc[5],
                            adp_channel_from_bc[6]
                        ))
            else:
                self.update_failed_command(command)

    def update_failed_command(self, command):
        command.command_status = BCCommandsStatus.FAILED.value
        flag_modified(command, "command_status")
        command.update_db()
        return

    def update_inprocess_command(self, command):
        command.command_status = BCCommandsStatus.INPROCESS.value
        flag_modified(command, "command_status")
        command.update_db()
        return

    def update_command_on_db(self, command):
        command.command_status = BCCommandsStatus.READY.value
        flag_modified(command, "command_status")
        command.update_db()
        return
