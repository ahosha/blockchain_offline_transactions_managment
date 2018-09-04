# Flask settings

FLASK_DEBUG = False  # Do not use debug mode in production

FLASK_SERVER_HOST = '0.0.0.0'
FLASK_SERVER_HOST_DEBUG = '127.0.0.1'
FLASK_SERVER_PORT = '80'
FLASK_SERVER_PORT_DEBUG = '4995'

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# SQLAlchemy settings
SQLALCHEMY_DATABASE_HOST = 'itps-staging.ctyhtso2qejb.us-east-1.rds.amazonaws.com'
SQLALCHEMY_DATABASE_PORT = '5432'
SQLALCHEMY_DATABASE_DATABASE = 'itps_staging'
SQLALCHEMY_DATABASE_USER = 'itps_admin'
SQLALCHEMY_DATABASE_PASSWORD = 'itps_admin'
SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# ___________________ BC Setting ____________________


ITPS_SERVICE_ADDRESS = '0x6C9EcaD3fF968Fc533f44AeCeC19eBF8FA628c24'
ITPS_SERVICE_PRIVATE_KEY = 'F9F80EEAB54199815B26ADD21CAFFB5B5747924DE529C6E9B6B7320B17A4D203'

NODE_PROTOCOL = 'HTTP'
NODE_PORT = '8545'
NODE_HOST = '172.31.20.250'

ADPCHANNEL_MANAGER_ADDRESS = '0x7Ab441a62790F170dD8C604745A21c2B6faB7Df7'
ADPCHANNEL_MANAGER_JSON = 'ADPChannelManager.json'
ADPCHANNEL_JSON = 'ADPChannel.json'
ERC20_TOKEN_JSON = 'ERC20Token.json'



# replace with real CLIENT_SYSTEM_ADDRESS for production
CLIENT_SYSTEM_ADDRESS = '0x6C9EcaD3fF968Fc533f44AeCeC19eBF8FA628c24'
TRX_GRACETIME = 0

GAS_PRICE = 20000000000
# GAS_PRICE * 1000
GAS_LIMIT_CHANNEL_CREATION = 2000000
GAS_LIMIT_WITHDRAW = 2000000
GAS_LIMIT_SETTLEMENT = 2000000

EMPTY_CHANNEL = '0x0000000000000000000000000000000000000000'
TRANSFER_EVENT_NAME = 'Transfer'
SETTLEMENT_EVENT_NAME = 'Settlement'
TOKEN_DEPOSIT_EVENT_NAME = "token_deposit"
TOKEN_WITHDRAW_EVENT_NAME = "token_withdrawal"

BC_MONITOR_INTERVAL = 10

SEND_CALLBACK = 0

# _________________________________Debug Settings_______________________
TRANSFER_AMOUNT = 100


