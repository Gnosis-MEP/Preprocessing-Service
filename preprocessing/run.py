#!/usr/bin/env python
from event_service_utils.streams.redis import RedisStreamFactory

from preprocessing.service import PreProcessing

from preprocessing.conf import (
    REDIS_ADDRESS,
    REDIS_PORT,
    RUN_STREAM_TO_BUFFERS,
    SERVICE_STREAM_KEY,
    SERVICE_CMD_KEY,
    LOGGING_LEVEL
)


def run_service():
    stream_factory = RedisStreamFactory(host=REDIS_ADDRESS, port=REDIS_PORT)
    service = PreProcessing(
        service_stream_key=SERVICE_STREAM_KEY,
        service_cmd_key=SERVICE_CMD_KEY,
        stream_to_buffers_bin=RUN_STREAM_TO_BUFFERS,
        stream_factory=stream_factory,
        logging_level=LOGGING_LEVEL
    )
    service.run()


def main():
    try:
        run_service()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
