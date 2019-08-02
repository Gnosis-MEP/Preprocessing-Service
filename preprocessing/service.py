import subprocess
import threading

import uuid
import re

from event_service_utils.schemas.events import BaseEventMessage
from event_service_utils.schemas.internal_msgs import (
    BaseInternalMessage,
    MatchingEngineUpdateSubscriberMessage,
)

from preprocessing.base import BaseService
# from preprocessing.publishers import run_publisher


class PreProcessing(BaseService):
    def __init__(self,
                 service_stream_key, service_cmd_key,
                 um_stream_key,
                 run_publishers_bin,
                 stream_factory):

        super(PreProcessing, self).__init__(
            name=self.__class__.__name__,
            service_stream_key=service_stream_key,
            service_cmd_key=service_cmd_key,
            cmd_event_schema=BaseInternalMessage,
            stream_factory=stream_factory
        )

        self.run_publishers_bin = run_publishers_bin
        self.stream_factory = stream_factory
        self.um_stream_key = um_stream_key
        self.service_stream = self.stream_factory.create(service_stream_key)
        self.service_cmd = self.stream_factory.create(service_cmd_key, stype='streamOnly')

        self.publishers = {}

    def run_virtual_publisher_process(self, action):
        # import ipdb; ipdb.set_trace()
        url = 'rtmp://localhost/live/mystream'
        frame_skip_n = 5
        url, frame_skip_n = action.split('-')
        # publisher_cleanup = url.replace('/', '-').replace(':', '-')
        # user_id = f'{publisher_cleanup}-skip{frame_skip_n}'
        # self.publisher_thread = threading.Thread(
        #     target=run_publisher,
        #     args=(user_id, self.stream_factory, self.um_stream_key, url, frame_skip_n)
        # )
        # self.publishers[url] = True
        # self.publisher_thread.start()
        # self.publisher_thread.join()
        # p1 = subprocess.Process(
        #     target=run_publisher,
        #     args=(user_id, self.stream_factory, self.um_stream_key, url, frame_skip_n)
        # )
        p = subprocess.Popen(['python', self.run_publishers_bin, url, str(frame_skip_n)])
        print(p)

    def process_events(self):
        self.logger.debug('Processing EVENTS..')
        if not self.service_stream:
            return
        event_list = self.service_stream.read_events(count=1)
        for event_tuple in event_list:
            msg_id, json_msg = event_tuple
            event_schema = BaseEventMessage(json_msg=json_msg)
            event_data = event_schema.object_load_from_msg()

    def process_action(self, action, event_data, json_msg):
        super(PreProcessing, self).process_action(action, event_data, json_msg)
        if len(self.publishers) == 0:
            self.run_virtual_publisher_process(action)

        # if action in ['subJoin', 'subLeave']:
        #     event_schema = MatchingEngineUpdateSubscriberMessage(json_msg=json_msg)
        #     event_data = event_schema.object_load_from_msg()
        #     if action == 'subJoin':
        #         self.add_subscriber(event_data['uid'], event_data['sub_id'], event_data['subscription'])
        #     elif action == 'subLeave':
        #         self.rm_subscriber(event_data['uid'])

    def _log_dict(self, dict_name, dict):
        log_msg = f'- {dict_name}:'
        for k, v in dict.items():
            log_msg += f'\n-- {k}  ---  {v}'
        self.logger.debug(log_msg)

    def log_state(self):
        super(PreProcessing, self).log_state()
        # self._log_dict('Subscribers', self.subscribers)
        # self.logger.debug('Current Windows:')
        # for window in self.subscription_windows.values():
        #     window.log_status(self.logger)

    def run(self):
        super(PreProcessing, self).run()
        self.cmd_thread = threading.Thread(target=self.run_forever, args=(self.process_cmd,))
        self.event_thread = threading.Thread(target=self.run_forever, args=(self.process_events,))
        # self.run_virtual_publisher_thread()
        self.cmd_thread.start()
        self.event_thread.start()
        self.cmd_thread.join()
        self.event_thread.join()
