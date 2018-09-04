import logging

from flask import request
from flask_restplus import Resource
from src.api.service.serializers import account
from src.api.service.parsers import ext_account_id_arguments
from src.api.restplus import api

from src.business.channel import *

from src.database.models.command_model import Command
from src.common.bc_commands import BCCommands, BCCommandsStatus

log = logging.getLogger(__name__)

ns = api.namespace('accounts', description='ITPS account management')


@ns.route('/')
class AccountsCollection(Resource):

    @api.expect(ext_account_id_arguments, validate=True)
    @api.marshal_with(account)
    def get(self):
        """   Returns list of accounts or single account """
        args = ext_account_id_arguments.parse_args(request)
        ext_account_id = args.get('ext_account_id', 1)
        account_from_db = Account.find_by_ext_account_id(ext_account_id)
        if account_from_db:
            # account_to_returm = account()
            return account_from_db
        else:
            return None

    @api.expect(account, validate=True)
    @api.response(201, 'Account successfully created.')
    def post(self):
        """
        Creates a new ITPS account with external account id and public key provided
        Deploys Channel Contract. When this async operation (10-15 min) is complete, blockchain monitoring service will invoke callback ChannelState()
        """
        request_data = request.json
        input_token_address = request_data.get('token_address')
        user_public_key = request_data.get('user_public_key')
        external_account_id = request_data.get('ext_account_id')
        # sender_address_to_save = sender_address_from_request

        external_account = Account.find_by_ext_account_id(external_account_id)
        user_public_account = Account.find_by_user_public_key(user_public_key)

        if not external_account and not user_public_account:
            command_args = {}
            command_args['external_account_id'] = external_account_id
            command_args['input_token_address'] = input_token_address

            Command(command_name=BCCommands.CREATE_CHANNEL.name,
                    user_public_key=user_public_key,
                    command_status=BCCommandsStatus.TODO.value,
                    command_args=command_args).save_to_db()
        else:
            print("input duplication")
            return "input duplication", 500
        return None, 201
