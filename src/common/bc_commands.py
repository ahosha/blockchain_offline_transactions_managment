from enum import Enum


# SUPPORTED_BLOCKCHAIN_COMMANDS = ("create_channel","transfer","get_decimals","settlement","withdraw","sync_channel")
class BCCommands(Enum):
    CREATE_CHANNEL = 1
    TRANSFER = 2
    GET_DECIMAL = 3
    SETTLEMENT = 4
    WITHDRAW = 5
    SYNC_CHANNEL = 6



class BCCommandsStatus(Enum):
    TODO = 1
    READY = 2
    FAILED = 3
    INPROCESS = 4

