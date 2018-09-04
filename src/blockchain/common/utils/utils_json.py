import json
# import sha3 as _sha3


class Utils(object):

    @classmethod
    def read_json(cls, path):
        with open(path) as json_file:
            data = json.load(json_file)
            return data
