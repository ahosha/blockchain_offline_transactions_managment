import logging
import os
import json

from flask import request
from flask_restplus import Resource
from src.api.service.serializers import  channel_snapshot
from src.api.service.parsers import ext_account_id_arguments
from src.api.restplus import api
from src.database.models.channel_model import Channel


log = logging.getLogger(__name__)

ns = api.namespace('channels', description='Operations related to service channels')

@ns.route('/')
class ChannelsCollection(Resource):

    @api.expect(ext_account_id_arguments, validate=True)
    @api.marshal_list_with(channel_snapshot)
    def get(self):
        """   Returns list of channels or single channel"""
        args = ext_account_id_arguments.parse_args(request)
        ext_account_id = args.get('ext_account_id', 1)
        channels = Channel.find_by_ext_account_id(ext_account_id)
        if channels:
            return channels
        else:
            return None





