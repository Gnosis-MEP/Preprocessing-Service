#!/usr/bin/env python
import sys
from event_service_utils.pub_sub import Publisher
from event_service_utils.streams.redis import RedisStreamFactory
from preprocessing.event_generators import (
    ImageUploadFromRTMPEventGenerator
)

from preprocessing.conf import (
    REDIS_ADDRESS,
    REDIS_PORT,
    USER_MANAGER_STREAM_KEY,
    PREPROCESSING_STREAM_KEY,
    PREPROCESSING_CMD_KEY,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_ENDPOINT,
    MINIO_SECURE_CONNECTION,
)


def run_publisher(user_id, stream_factory, um_stream_key, media_source, frame_skip_n):
    minio_fs_cli_config = {
        'endpoint': MINIO_ENDPOINT,
        'access_key': MINIO_ACCESS_KEY,
        'secret_key': MINIO_SECRET_KEY,
        'secure': MINIO_SECURE_CONNECTION,
    }
    # event_generator = ImageRedisCacheFromMpeg4EventGenerator(redis_fs_cli_config, media_source, user_id)
    event_generator = ImageUploadFromRTMPEventGenerator(minio_fs_cli_config, media_source, user_id, frame_skip_n)
    pub = Publisher(user_id, stream_factory, um_stream_key, event_generator)
    pub.start()


def main():
    # source = 'rtmp://localhost/live/mystream'
    # frame_skip_n = 5
    source = sys.argv[1]
    frame_skip_n = int(sys.argv[2])

    publisher_cleanup = source.replace('/', '-').replace(':', '-')
    user_id = f'{publisher_cleanup}-skip{frame_skip_n}'
    stream_factory = RedisStreamFactory(host=REDIS_ADDRESS, port=REDIS_PORT)
    try:
        run_publisher(user_id, stream_factory, USER_MANAGER_STREAM_KEY, source, frame_skip_n)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
