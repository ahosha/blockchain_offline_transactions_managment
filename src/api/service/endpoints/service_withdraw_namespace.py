import logging
from flask import request
from flask_restplus import Resource
from src.api.service.parsers import ext_account_id_arguments
from src.api.restplus import api
from src.business.business import *
from src.database.models.command_model import Command
from src.common.bc_commands import BCCommands, BCCommandsStatus


log = logging.getLogger(__name__)

ns = api.namespace('withdraw', description='Operations related to settlement')


@ns.route('/')
class Withdraw(Resource):

    @api.expect(ext_account_id_arguments, validate=True)
    def post(self):
        """
        Initiates a new withdrawal.
        """
        args = ext_account_id_arguments.parse_args(request)
        ext_account_id = args.get('ext_account_id', 1)
        account_from_db = Account.find_by_ext_account_id(ext_account_id)
        if account_from_db:
            address_sender = account_from_db.user_public_key
            token_address = account_from_db.token_address
        else:
            return None

        if address_sender:
            command_args = {}
            command_args['token_address'] = token_address

            Command(command_name=BCCommands.WITHDRAW.name,
                    user_public_key=address_sender,
                    command_status=BCCommandsStatus.TODO.value,
                    command_args=command_args).save_to_db()
        return None, 201



