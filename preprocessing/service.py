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
                 um_stream_key,
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
        self.stream_factory = stream_factory
        self.um_stream_key = um_stream_key
        self.service_stream = self.stream_factory.create(service_stream_key)
        self.service_cmd = self.stream_factory.create(service_cmd_key, stype='streamOnly')

        self.buffers = {}

    def _run_subprocess(self, *args):
        self.logger.debug(f'Starting subprocess with args: {args}')
        p = subprocess.Popen(*args)
        return p

    def start_preprocessing_for_buffer_stream(self, source, resolution, fps, buffer_stream_key):
        # source = 'rtmp://localhost/live/mystream'
        # frame_skip_n = 5
        # url, frame_skip_n = action.split('-')

        preprocessing_data = {
            'source': source,
            'resolution': resolution,
            'fps': fps,
            'buffer_stream_key': buffer_stream_key,
        }
        self.logger.info(f'Starting preprocessing for: {buffer_stream_key}. Buffer data: {preprocessing_data}')
        p = self._run_subprocess(['python', self.stream_to_buffers_bin, source, str(fps), buffer_stream_key])
        preprocessing_data['subprocess'] = p
        self.buffers.update({buffer_stream_key: preprocessing_data})

    def stop_preprocessing_for_buffer_stream(self, buffer_stream_key):
        preprocessing_data = self.buffers.get(buffer_stream_key, None)
        if preprocessing_data:
            self.logger.info(f'Stoping preprocessing for: {buffer_stream_key}. Buffer data: {preprocessing_data}')
            subprocess = preprocessing_data['subprocess']
            subprocess.kill()

    def process_events(self):
        self.logger.debug('Processing EVENTS..')
        if not self.service_stream:
            return
        event_list = self.service_stream.read_events(count=1)
        for event_tuple in event_list:
            event_id, json_msg = event_tuple
            event_schema = self.cmd_event_schema(json_msg=json_msg)
            event_data = event_schema.object_load_from_msg()
            action = event_data['action']
            self.process_action(action, event_data, json_msg)
            self.log_state()

    def process_action(self, action, event_data, json_msg):
        super(PreProcessing, self).process_action(action, event_data, json_msg)
        if action == 'startPreprocessing':
            source = event_data['source']
            resolution = event_data['resolution']
            fps = event_data['fps']
            buffer_stream_key = event_data['buffer_stream_key']
            self.start_preprocessing_for_buffer_stream(source, resolution, fps, buffer_stream_key)
        elif action == 'stopPreprocessing':
            buffer_stream_key = event_data['buffer_stream_key']
            self.stop_preprocessing_for_buffer_stream(buffer_stream_key)

    def log_state(self):
        super(PreProcessing, self).log_state()
        self._log_dict('Buffers', self.buffers)

    def run(self):
        super(PreProcessing, self).run()
        # self.cmd_thread = threading.Thread(target=self.run_forever, args=(self.process_cmd,))
        self.event_thread = threading.Thread(target=self.run_forever, args=(self.process_events,))
        # self.run_virtual_publisher_thread()
        # self.cmd_thread.start()
        self.event_thread.start()
        # self.cmd_thread.join()
        self.event_thread.join()
