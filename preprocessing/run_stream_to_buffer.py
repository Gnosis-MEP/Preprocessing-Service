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
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_ENDPOINT,
    MINIO_SECURE_CONNECTION,
    FFMPEG_BIN,
)


def run_stream_to_buffer(stream_factory, um_stream_key, media_source, width, height, fps, buffer_stream_key, ffmpeg):
    minio_fs_cli_config = {
        'endpoint': MINIO_ENDPOINT,
        'access_key': MINIO_ACCESS_KEY,
        'secret_key': MINIO_SECRET_KEY,
        'secure': MINIO_SECURE_CONNECTION,
    }
    event_generator = ImageUploadFromRTMPEventGenerator(
        minio_fs_cli_config, media_source, width, height, fps, buffer_stream_key, ffmpeg)
    pub = Publisher(buffer_stream_key, stream_factory, um_stream_key, event_generator)
    pub.start()


def main():
    # source = 'rtmp://localhost/live/mystream'
    # frame_skip_n = 5
    media_source = sys.argv[1]
    width = int(sys.argv[2])
    height = int(sys.argv[3])
    fps = int(sys.argv[4])
    buffer_stream_key = sys.argv[5]
    stream_factory = RedisStreamFactory(host=REDIS_ADDRESS, port=REDIS_PORT)
    try:
        run_stream_to_buffer(
            stream_factory, USER_MANAGER_STREAM_KEY, media_source, width, height, fps, buffer_stream_key, FFMPEG_BIN)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
