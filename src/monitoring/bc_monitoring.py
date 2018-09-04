import os
from src.database.models.bc_monitor_model import BCMonitor
from src.blockchain.service.blockchain_service import BlockChainService
from src.common.singleton_decorator import singleton
from src.common.settings import *
from src.callback.call_back_service import CallBackService
from src.database.models.channel_model import Channel
from src.database.models.account_model import Account
from src.database.models.token_model import Token
from sqlalchemy.orm.attributes import flag_modified
from src.database.models.withdraw_model import Withdraw
from src.database.models.settlement_model import Settlement
from src.blockchain.common.utils.utils_json import Utils
from src.blockchain.common.utils.utils_bc import *
import sys, traceback


@singleton
class BCMonitorService:
    token_address = None
    token_abi = None
    adp_channel_manager_address = None
    adp_channel_manager_abi = None
    event_monitor = None
    latest_block_number = None
    blockchain_service = None

    def __init__(self):
        adp_channel_manager_path, adp_channel_path, token_abi_path = self.get_json_pathes()
        channel_manager_json = Utils.read_json(adp_channel_manager_path)
        channel_json = Utils.read_json(adp_channel_path)
        token_abi = Utils.read_json(token_abi_path)
        # print('bc_monitor.create BlockChainService->token_abi:{}'.format(token_abi))
        # print('bc_monitor.create BlockChainService->channel_manager_abi:{}'.format(channel_manager_json["abi"]))
        # print('bc_monitor.create BlockChainService->channel_abi:{}'.format(channel_json["abi"]))

        self.blockchain_service = BlockChainService(token_abi=token_abi,
                                                    adp_channel_manager_address=ADPCHANNEL_MANAGER_ADDRESS,
                                                    adp_channel_manager_abi=channel_manager_json["abi"],
                                                    adp_channel_abi=channel_json["abi"])

    def monitor(self, app):
        latest_block_number_from_bc = self.blockchain_service.get_latest_block_number()
        latest_block_from_db = BCMonitor.find_by_last_block()
        if not latest_block_from_db:
            if latest_block_number_from_bc - 100 > 0:
                latest_block_to_scan = latest_block_number_from_bc - 100
            else:
                latest_block_to_scan = 0
            latest_block_from_db = BCMonitor(latest_block=latest_block_to_scan)
            latest_block_from_db.save_to_db()
        if latest_block_from_db.latest_block != latest_block_number_from_bc:
            tokens_for_monitor = Token.get_all_tokens()
            for token in tokens_for_monitor:
                event_monitor = self.blockchain_service.create_event_monitor(token.token_address)
                self.do_token_events_monitor(event_monitor, latest_block_from_db.latest_block)
            self.do_channel_manager_events_monitor(latest_block_from_db.latest_block)
            latest_block_from_db.latest_block = latest_block_number_from_bc
            latest_block_from_db.update_db()
        return

    def save_latest_block_to_db(self, monitor,
                                latest_block_number_from_bc):
        try:
            self.update_bc_monitor_db(monitor, latest_block_number_from_bc)
        except Exception as e:
            print('Failed to save_latest_block_to_db: ' + str(e))
            bcmonitor = BCMonitor(latest_block=latest_block_number_from_bc)
            bcmonitor.save_to_db()

    def do_token_events_monitor(self, event_monitor, from_block):
        try:
            token_events = event_monitor.get_token_events(from_block)
            self.handle_token_events(token_events)
            return
        except Exception as expected:
            traceback.print_exc()
            # e = sys.exc_info()[0]
            # print('do_token_events_monitor Error: %s' % e)
            return

    def do_channel_manager_events_monitor(self, from_block):
        try:
            channel_manager_events = self.blockchain_service.get_channel_manager_events(from_block)
            self.handle_channel_manager_events(channel_manager_events)
            return
        except Exception as expected:
            traceback.print_exc()
            # e = sys.exc_info()[0]
            # print('do_channel_manager_events_monitor Error: %s' % e)
            return

    def handle_channel_manager_events(self, channel_manager_events):
        """
        call callback post.channel state
        settlement (from, nonce, withdrawalAmount, settlementType)
        :param channel_manager_events:
        :return:
        """
        print('received {} channel manager events'.format(str(len(channel_manager_events))))
        for event in channel_manager_events:
            event_args = {}
            event_args['contractAddress'] = event.args.contractAddress
            event_args['from'] = event.args.fromAddress
            event_args['nonce'] = event.args.nonce
            event_args['withdrawalAmount'] = event.args.withdrawalAmount
            event_args['settlementType'] = event.args.settlementType
            CallBackService().post_client_system_callback_channel_state(event="settlement",
                                                                        event_args_dict_json=event_args)
            channel = Channel.find_by_channel_address(event.args.contractAddress)
            if channel:
                Settlement(channel.ext_account_id, channel.sender_withdrawable).save_to_db()

    def handle_token_events(self, token_events):
        """
        check from args "to" to detect deposit with our channel_address  token_deposit
        token_deposit ( amount, from )
        check from args "from" to detect withdraw with our channel_address  token_withdrawal
        token_withdrawal ( amount, to )
        call callback
        :param token_events:
        :return:
        """
        print('received {} token events'.format(str(len(token_events))))
        for event in token_events:
            print()
            channel_address = event.args.to
            event_name = TOKEN_DEPOSIT_EVENT_NAME
            self.send_token_call_back(channel_address, event, event_name)

            channel_address = next(iter(event.args.values()))
            event_name = TOKEN_WITHDRAW_EVENT_NAME
            self.send_token_call_back(channel_address, event, event_name)

    def send_token_call_back(self, channel_address, event, event_name):
        channel = Channel.find_by_channel_address(channel_address)
        if channel:
            account = Account.find_by_ext_account_id(channel.ext_account_id)
            channel_state_from_bc = self.blockchain_service.get_adp_channel_bc_by_channel_address(channel_address,
                                                                                                  channel.user_public_key)
            if channel_state_from_bc:
                update_channel_on_db(channel_from_db=channel,
                                     adp_channel_from_bc=channel_state_from_bc,
                                     token_address=account.token_address)
                # invoke callback with event args
                event_args = {}
                if event_name == TOKEN_DEPOSIT_EVENT_NAME:
                    self.next = next(iter(event.args.values()))
                    event_args['from'] = self.next
                if event_name == TOKEN_WITHDRAW_EVENT_NAME:
                    event_args['to'] = event.args.to
                    # save withdraw in db
                    Withdraw(channel.ext_account_id).save_to_db()
                event_args['amount'] = event.args.value
                CallBackService().post_client_system_callback_channel_state(event=event_name,
                                                                            event_args_dict_json=event_args)

    def update_bc_monitor_db(self, bc_monitor, new_latest_block):
        # if not bc_monitor:
        #     bc_monitor = BCMonitor(latest_block)
        #     bc_monitor.save_to_db()
        # else:
        bc_monitor.delete_from_db()
        new_monitor = BCMonitor(latest_block=new_latest_block)
        new_monitor.save_to_db()
        # bc_monitor.latest_block = new_latest_block
        # flag_modified(bc_monitor, "latest_block")
        # bc_monitor.update_db()

    def get_json_pathes(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        token_abi_path = os.path.join(my_path, "../blockchain/common/ABI/{}".format(ERC20_TOKEN_JSON))
        adp_channel_manager_path = os.path.join(my_path,
                                                "../blockchain/common/ABI/{}".format(ADPCHANNEL_MANAGER_JSON))
        adp_channel_path = os.path.join(my_path, "../blockchain/common/ABI/{}".format(ADPCHANNEL_JSON))
        return adp_channel_manager_path, adp_channel_path, token_abi_path
