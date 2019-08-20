import subprocess
import threading

from event_service_utils.services.base import BaseService
# from event_service_utils.schemas.events import BaseEventMessage
from event_service_utils.schemas.internal_msgs import (
    BaseInternalMessage,
)


class PreProcessing(BaseService):
    def __init__(self,
                 service_stream_key, service_cmd_key,
                 stream_to_buffers_bin,
                 stream_factory,
                 logging_level):

        super(PreProcessing, self).__init__(
            name=self.__class__.__name__,
            service_stream_key=service_stream_key,
            service_cmd_key=service_cmd_key,
            cmd_event_schema=BaseInternalMessage,
            stream_factory=stream_factory,
            logging_level=logging_level
        )

        self.stream_to_buffers_bin = stream_to_buffers_bin
        self.buffers = {}

    def _prepare_subprocess_arglist(self, publisher_id, source, resolution, fps, buffer_stream_key):
        width, height = resolution.split('x')
        return ['python', self.stream_to_buffers_bin, publisher_id, source, width, height, str(fps), buffer_stream_key]

    def _run_subprocess(self, *args):
        self.logger.debug(f'Starting subprocess with args: {args}')
        p = subprocess.Popen(*args)
        return p

    def start_preprocessing_for_buffer_stream(self, publisher_id, source, resolution, fps, buffer_stream_key):
        # source = 'rtmp://localhost/live/mystream'
        # frame_skip_n = 5
        # url, frame_skip_n = action.split('-')

        preprocessing_data = {
            'publisher_id': publisher_id,
            'source': source,
            'resolution': resolution,
            'fps': fps,
            'buffer_stream_key': buffer_stream_key,
        }
        self.logger.info(f'Starting preprocessing for: {buffer_stream_key}. Buffer data: {preprocessing_data}')
        arg_list = self._prepare_subprocess_arglist(publisher_id, source, resolution, fps, buffer_stream_key)
        p = self._run_subprocess(arg_list)
        preprocessing_data['subprocess'] = p
        self.buffers.update({buffer_stream_key: preprocessing_data})

    def stop_preprocessing_for_buffer_stream(self, buffer_stream_key):
        preprocessing_data = self.buffers.get(buffer_stream_key, None)
        if preprocessing_data:
            self.logger.info(f'Stoping preprocessing for: {buffer_stream_key}. Buffer data: {preprocessing_data}')
            subprocess = preprocessing_data['subprocess']
            subprocess.kill()

    def process_action(self, action, event_data, json_msg):
        super(PreProcessing, self).process_action(action, event_data, json_msg)
        if action == 'startPreprocessing':
            publisher_id = event_data['publisher_id']
            source = event_data['source']
            resolution = event_data['resolution']
            fps = event_data['fps']
            buffer_stream_key = event_data['buffer_stream_key']
            self.start_preprocessing_for_buffer_stream(publisher_id, source, resolution, fps, buffer_stream_key)
        elif action == 'stopPreprocessing':
            buffer_stream_key = event_data['buffer_stream_key']
            self.stop_preprocessing_for_buffer_stream(buffer_stream_key)

    def log_state(self):
        super(PreProcessing, self).log_state()
        self._log_dict('Buffers', self.buffers)

    def run(self):
        super(PreProcessing, self).run()
        self.run_forever(self.process_cmd)
