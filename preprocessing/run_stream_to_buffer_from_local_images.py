#!/usr/bin/env python
import sys
from opentracing.ext import tags
from opentracing.propagation import Format

from event_service_utils.streams.redis import RedisStreamFactory
from event_service_utils.services.tracer import EVENT_ID_TAG
from event_service_utils.tracing.jaeger import init_tracer
from preprocessing.event_generators import (
    ImageUploadFromLocalImagesEventGenerator
)

from preprocessing.conf import (
    REDIS_ADDRESS,
    REDIS_PORT,
    REDIS_EXPIRATION_TIME,
    TRACER_REPORTING_HOST,
    TRACER_REPORTING_PORT,
)


class PublishToBuffer():

    def __init__(self, buffer_stream_key, stream_factory, event_generator, tracer):
        self.buffer_stream_key = buffer_stream_key
        self.stream_factory = stream_factory
        self.stream = self.stream_factory.create(self.buffer_stream_key)
        self.event_generator = event_generator
        self.tracer = tracer

    def inject_current_tracer_into_event_data(self, event_data):
        tracer_data = event_data.setdefault('tracer', {})
        tracer_headers = tracer_data.setdefault('headers', {})
        tracer_tags = {
            EVENT_ID_TAG: event_data['id'],
        }
        with self.tracer.start_active_span('tracer_injection') as scope:
            for tag, value in tracer_tags.items():
                scope.span.set_tag(tag, value)
            self.tracer.inject(scope.span, Format.HTTP_HEADERS, tracer_headers)
        return event_data

    def publish_next_event(self):
        event_schema = self.event_generator.next_event()
        if event_schema is not None:
            tracer_tags = {
                tags.MESSAGE_BUS_DESTINATION: self.buffer_stream_key,
                tags.SPAN_KIND: tags.SPAN_KIND_PRODUCER,
                EVENT_ID_TAG: event_schema.dict['id'],
            }
            with self.tracer.start_active_span('publish_next_event', child_of=None) as scope:
                for tag, value in tracer_tags.items():
                    scope.span.set_tag(tag, value)
                event_schema.dict = self.inject_current_tracer_into_event_data(event_schema.dict)
                msg_json = event_schema.json_msg_load_from_dict()
                self.stream.write_events(msg_json)

    def start(self):
        try:
            while True:
                self.publish_next_event()
        finally:
            self.stop()

    def stop(self):
        pass


def run_stream_to_buffer(
        stream_factory, publisher_id, images_dir, width, height, fps, buffer_stream_key, query_ids, expiration_time, tracer_configs):
    redis_fs_cli_config = {
        'host': REDIS_ADDRESS,
        'port': REDIS_PORT,
        'db': 0,
    }
    sub_service_name = 'PreProcessing'
    tracer = init_tracer(sub_service_name, **tracer_configs)
    event_generator = ImageUploadFromLocalImagesEventGenerator(
        redis_fs_cli_config, publisher_id, images_dir, width, height, fps, query_ids, expiration_time)
    pub_buffer = PublishToBuffer(buffer_stream_key, stream_factory, event_generator, tracer)
    pub_buffer.start()


def main():
    # source = 'rtmp://localhost/live/mystream'
    # frame_skip_n = 5
    publisher_id = sys.argv[1]
    images_dir = sys.argv[2]
    width = int(sys.argv[3])
    height = int(sys.argv[4])
    fps = float(sys.argv[5])
    buffer_stream_key = sys.argv[6]
    query_ids = sys.argv[7].split(',')
    stream_factory = RedisStreamFactory(host=REDIS_ADDRESS, port=REDIS_PORT)
    tracer_configs = {
        'reporting_host': TRACER_REPORTING_HOST,
        'reporting_port': TRACER_REPORTING_PORT,
    }
    try:
        run_stream_to_buffer(
            stream_factory, publisher_id, images_dir, width, height, fps, buffer_stream_key, query_ids, REDIS_EXPIRATION_TIME, tracer_configs)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
