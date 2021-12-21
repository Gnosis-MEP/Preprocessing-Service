import subprocess

from event_service_utils.services.event_driven import BaseEventDrivenCMDService
from event_service_utils.tracing.jaeger import init_tracer


class PreProcessing(BaseEventDrivenCMDService):
    def __init__(self,
                 service_stream_key, service_cmd_key_list,
                 pub_event_list, service_details,
                 stream_factory,
                 stream_to_buffers_bin,
                 logging_level,
                 tracer_configs):

        tracer = init_tracer(self.__class__.__name__, **tracer_configs)
        super(PreProcessing, self).__init__(
            name=self.__class__.__name__,
            service_stream_key=service_stream_key,
            service_cmd_key_list=service_cmd_key_list,
            pub_event_list=pub_event_list,
            service_details=service_details,
            stream_factory=stream_factory,
            logging_level=logging_level,
            tracer=tracer,
        )

        self.stream_to_buffers_bin = stream_to_buffers_bin
        self.buffers = {}

    def _prepare_subprocess_arglist(self, publisher_id, source, resolution, fps, buffer_stream_key, query_ids):
        comma_separated_query_ids = ','.join(query_ids)
        width, height = resolution.lower().split('x')
        return [
            'python', self.stream_to_buffers_bin, publisher_id, source, width, height, str(
                fps), buffer_stream_key, comma_separated_query_ids
        ]

    def _run_subprocess(self, *args):
        self.logger.debug(f'Starting subprocess with args: {args}')
        # p = subprocess.Popen(*args)
        p = None
        return p

    def start_preprocessing_for_buffer_stream(
            self, publisher_id, source, resolution, fps, buffer_stream_key, query_ids):
        # source = 'rtmp://localhost/live/mystream'
        # frame_skip_n = 5
        # url, frame_skip_n = action.split('-')

        preprocessing_data = {
            'publisher_id': publisher_id,
            'source': source,
            'resolution': resolution,
            'fps': fps,
            'buffer_stream_key': buffer_stream_key,
            'query_ids': query_ids
        }
        self.logger.info(f'Starting preprocessing for: {buffer_stream_key}. Buffer data: {preprocessing_data}')
        arg_list = self._prepare_subprocess_arglist(publisher_id, source, resolution, fps, buffer_stream_key, query_ids)
        p = self._run_subprocess(arg_list)
        preprocessing_data['subprocess'] = p
        self.buffers.update({buffer_stream_key: preprocessing_data})

    def stop_preprocessing_for_buffer_stream(self, buffer_stream_key):
        preprocessing_data = self.buffers.get(buffer_stream_key, None)
        if preprocessing_data:
            self.logger.info(f'Stoping preprocessing for: {buffer_stream_key}. Buffer data: {preprocessing_data}')
            subprocess = preprocessing_data['subprocess']
            subprocess.kill()

    def process_event_type(self, event_type, event_data, json_msg):
        if not super(PreProcessing, self).process_event_type(event_type, event_data, json_msg):
            return False

        if event_type == 'QueryCreated':
            buffer_stream = event_data['buffer_stream']
            publisher_id = buffer_stream['publisher_id']
            source = buffer_stream['source']
            resolution = buffer_stream['resolution']
            fps = buffer_stream['fps']
            buffer_stream_key = buffer_stream['buffer_stream_key']
            # for now only considers one query per bufferstream
            # at some point a change in the preprocesssor has to be done
            # to facilitate updating the ffmpeg sub-process update to add new query ids
            # to the published events.
            query_ids = [event_data['query_id']]
            self.start_preprocessing_for_buffer_stream(
                publisher_id, source, resolution, fps, buffer_stream_key, query_ids)
        elif event_type == 'QueryRemoved':
            buffer_stream = event_data['buffer_stream']
            buffer_stream_key = buffer_stream['buffer_stream_key']
            self.stop_preprocessing_for_buffer_stream(buffer_stream_key)

    def log_state(self):
        super(PreProcessing, self).log_state()
        self._log_dict('Buffers', self.buffers)

    def run(self):
        super(PreProcessing, self).run()
        self.run_forever(self.process_cmd)
