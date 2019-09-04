import json


class EventVEkgMessage():

    def __init__(self, id=None, publisher_id=None, source=None, image_url=None, vekg=None, json_msg=None):
        self.dict = {
            'id': id,
            'publisher_id': publisher_id,
            'source': source,
            'image_url': image_url,
            'vekg': vekg,
        }
        self.json_serialized = json_msg

    def json_msg_load_from_dict(self):
        if self.dict['id'] is None:
            self.dict['id'] = ''
        if self.dict['vekg'] is None:
            self.dict['vekg'] = {}

        self.json_serialized = {
            'event': json.dumps(self.dict)
        }
        return self.json_serialized

    def object_load_from_msg(self):
        event_json = self.json_serialized.get(b'event', '{}')
        self.dict = json.loads(event_json)
        if self.dict['id'] is None:
            self.dict['id'] = ''
        if self.dict['vekg'] is None:
            self.dict['vekg'] = {}

        return self.dict
