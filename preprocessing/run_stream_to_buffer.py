#!/usr/bin/env python
import sys
from event_service_utils.streams.redis import RedisStreamFactory
from preprocessing.event_generators import (
    ImageUploadFromRTMPEventGenerator
)

from preprocessing.conf import (
    REDIS_ADDRESS,
    REDIS_PORT,
    FFMPEG_BIN,
    REDIS_EXPIRATION_TIME,
)


class PublishToBuffer():

    def __init__(self, buffer_stream_key, stream_factory, event_generator):
        self.buffer_stream_key = buffer_stream_key
        self.stream_factory = stream_factory
        self.stream = self.stream_factory.create(self.buffer_stream_key)
        self.event_generator = event_generator

    def publish_next_event(self):
        event_data = self.event_generator.next_event()
        self.stream.write_events(event_data)

    def start(self):
        try:
            while True:
                self.publish_next_event()
        finally:
            self.stop()

    def stop(self):
        pass


def run_stream_to_buffer(
        stream_factory, publisher_id, media_source, width, height, fps, buffer_stream_key, ffmpeg, expiration_time):
    redis_fs_cli_config = {
        'host': REDIS_ADDRESS,
        'port': REDIS_PORT,
        'db': 0,
    }
    event_generator = ImageUploadFromRTMPEventGenerator(
        redis_fs_cli_config, publisher_id, media_source, width, height, fps, ffmpeg, expiration_time)
    pub_buffer = PublishToBuffer(buffer_stream_key, stream_factory, event_generator)
    pub_buffer.start()


def main():
    # source = 'rtmp://localhost/live/mystream'
    # frame_skip_n = 5
    publisher_id = sys.argv[1]
    media_source = sys.argv[2]
    width = int(sys.argv[3])
    height = int(sys.argv[4])
    fps = int(sys.argv[5])
    buffer_stream_key = sys.argv[6]
    stream_factory = RedisStreamFactory(host=REDIS_ADDRESS, port=REDIS_PORT)
    try:
        run_stream_to_buffer(
            stream_factory, publisher_id, media_source, width, height, fps, buffer_stream_key, FFMPEG_BIN, REDIS_EXPIRATION_TIME)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
