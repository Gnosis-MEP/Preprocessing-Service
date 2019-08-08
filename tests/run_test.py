#!/usr/bin/env python
from preprocessing.mocked_stream import MockedStreamFactory
from event_service_utils.streams.redis import RedisStreamFactory
from event_service_utils.schemas.internal_msgs import (
    BaseInternalMessage
)

from preprocessing.service import PreProcessing

from preprocessing.conf import (
    REDIS_ADDRESS,
    REDIS_PORT,
    USER_MANAGER_STREAM_KEY,
    PREPROCESSING_STREAM_KEY,
    PREPROCESSING_CMD_KEY,
)


def make_dict_key_bites(d):
    return {k.encode('utf-8'): v for k, v in d.items()}


def make_new_publisher_cmd(action):
    schema = BaseInternalMessage(action=action)
    return (
        None,
        make_dict_key_bites(schema.json_msg_load_from_dict())
    )


def run_service():
    stream_factory = MockedStreamFactory(
        mocked_dict={
            PREPROCESSING_STREAM_KEY: [],
            PREPROCESSING_CMD_KEY: [
                make_new_publisher_cmd('publish'),
            ],
            USER_MANAGER_STREAM_KEY: [],
        }
    )

    # stream_factory = RedisStreamFactory(host=REDIS_ADDRESS, port=REDIS_PORT)
    service = PreProcessing(
        service_stream_key=PREPROCESSING_STREAM_KEY,
        service_cmd_key=PREPROCESSING_CMD_KEY,
        um_stream_key=USER_MANAGER_STREAM_KEY,
        stream_factory=stream_factory
    )
    service.run()


def main():
    try:
        run_service()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
