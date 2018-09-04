from datetime import datetime
from src.common.singleton_decorator import singleton
from src.common.settings import *
from src.database.models.account_model import Account
from src.database.models.settlement_model import Settlement
from src.database.models.channel_model import Channel
from src.database.models.command_model import Command
from src.database.models.ccs_model import CurrentChannelState
from src.common.bc_commands import BCCommands, BCCommandsStatus
from datetime import timedelta
import math



@singleton
class DBMonitorService:

    def get_commands_to_do(self, app):
        try:
            return Command.find_by_command_status(BCCommandsStatus.TODO.value)
        except:
            return None

    def get_settlements_to_do(self, app):
        try:
            accounts = Account.get_all_accounts()
            settlements_to_do = []
            for account in accounts:
                channel = Channel.find_by_ext_account_id(account.ext_account_id)
                if channel:
                    if channel.receiver_withdrawable >=AUTO_SETTLEMENT_AMOUNT:
                        settlements_to_do.append(account.ext_account_id)
                    else:
                        settlement = Settlement.find_by_ext_account_id(account.ext_account_id)
                        if settlement:
                            settlement_date = settlement.time_created
                            if settlement_date:
                                time_difference = datetime.datetime.now() - settlement_date
                                time_difference_in_hours = time_difference / timedelta(hours=1)
                        else:
                            time_difference_in_hours = SCHEDULED_SETTLEMENT_PERIOD
                        if not settlement or time_difference_in_hours>=SCHEDULED_SETTLEMENT_PERIOD:
                                ccs = CurrentChannelState.find_by_ext_account_id(account.ext_account_id)
                                if ccs:
                                    #AvailableForSettlementToReceiver =  CCS.TotalPaidToReceiver-TotalWithdrawedByReceiver-Receiver Withdrawable
                                    available_for_settlement_to_receiver = ccs.total_paid_to_receiver-channel.total_withdrawed_by_receiver-channel.receiver_withdrawable
                                    if available_for_settlement_to_receiver >= MIN_SETTLEMENT_AMOUNT:
                                        settlements_to_do.append(account.ext_account_id)
            return settlements_to_do

        except:
            return None





