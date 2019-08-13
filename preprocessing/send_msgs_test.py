#!/usr/bin/env python
import time

from event_service_utils.streams.redis import RedisStreamFactory
from event_service_utils.schemas.internal_msgs import (
    BaseInternalMessage,
)

from preprocessing.conf import (
    REDIS_ADDRESS,
    REDIS_PORT,
    USER_MANAGER_STREAM_KEY,
    PREPROCESSING_STREAM_KEY,
    PREPROCESSING_CMD_KEY,
)


def make_dict_key_bites(d):
    return {k.encode('utf-8'): v for k, v in d.items()}


def new_action_msg(action, event_data):
    schema = BaseInternalMessage(action=action)
    schema.dict.update(event_data)
    return schema.json_msg_load_from_dict()


def send_msgs(service_stream):
    msg_1 = new_action_msg(
        'startPreprocessing',
        {
            'source': 'rtmp://localhost/live/mystream',
            'resolution': '640x480',
            'fps': '3',
            'buffer_stream_key': 'buffer-stream-key1',
        }
    )
    msg_2 = new_action_msg(
        'startPreprocessing',
        {
            'source': 'rtmp://localhost/live/mystream',
            'resolution': '320x240',
            'fps': '15',
            'buffer_stream_key': 'buffer-stream-key2',
        }
    )
    msg_3 = new_action_msg(
        'startPreprocessing',
        {
            'source': 'rtmp://localhost/live/mystream',
            'resolution': '640x480',
            'fps': '30',
            'buffer_stream_key': 'buffer-stream-key3',
        }
    )
    msg_4 = new_action_msg(
        'stopPreprocessing',
        {
            'buffer_stream_key': 'buffer-stream-key1',
        }
    )
    import ipdb; ipdb.set_trace()
    print(f'Sending msg {msg_1}')
    service_stream.write_events(msg_1)
    print(f'Sending msg {msg_2}')
    service_stream.write_events(msg_2)
    print(f'Sending msg {msg_3}')
    service_stream.write_events(msg_3)
    import ipdb; ipdb.set_trace()
    print(f'Sending msg {msg_4}')
    service_stream.write_events(msg_4)

def main():
    stream_factory = RedisStreamFactory(host=REDIS_ADDRESS, port=REDIS_PORT)
    service_stream = stream_factory.create(PREPROCESSING_STREAM_KEY, stype='streamOnly')
    send_msgs(service_stream)


if __name__ == '__main__':
    main()
