from flask_restplus import reqparse
from src.common.consts import *

ext_account_id_arguments = reqparse.RequestParser()

ext_account_id_arguments.add_argument('ext_account_id',
                                      type=str,
                                      required=False,
                                      default='account1',
                                      help=EXT_ACCOUMT_ID_FIELD_DESCRIPTION)




