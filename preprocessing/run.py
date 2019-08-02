#!/usr/bin/env python
from event_service_utils.streams.redis import RedisStreamFactory

from preprocessing.service import PreProcessing

from preprocessing.conf import (
    REDIS_ADDRESS,
    REDIS_PORT,
    RUN_PUBLISHERS_BIN,
    USER_MANAGER_STREAM_KEY,
    PREPROCESSING_STREAM_KEY,
    PREPROCESSING_CMD_KEY,
)


def run_service():
    stream_factory = RedisStreamFactory(host=REDIS_ADDRESS, port=REDIS_PORT)
    service = PreProcessing(
        service_stream_key=PREPROCESSING_STREAM_KEY,
        service_cmd_key=PREPROCESSING_CMD_KEY,
        um_stream_key=USER_MANAGER_STREAM_KEY,
        run_publishers_bin=RUN_PUBLISHERS_BIN,
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
