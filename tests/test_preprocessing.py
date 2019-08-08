from unittest.mock import patch

from event_service_utils.tests.base_test_case import MockedServiceStreamTestCase
from event_service_utils.tests.json_msg_helper import prepare_event_msg_tuple

from preprocessing.service import PreProcessing

from preprocessing.conf import (
    USER_MANAGER_STREAM_KEY,
    PREPROCESSING_STREAM_KEY,
    PREPROCESSING_CMD_KEY,
    RUN_STREAM_TO_BUFFERS,
)


class TestPreprocessing(MockedServiceStreamTestCase):
    GLOBAL_SERVICE_CONFIG = {
        'service_stream_key': PREPROCESSING_STREAM_KEY,
        'service_cmd_key': PREPROCESSING_CMD_KEY,
        'um_stream_key': USER_MANAGER_STREAM_KEY,
        'stream_to_buffers_bin': RUN_STREAM_TO_BUFFERS,
        'logging_level': 'DEBUG'
    }
    SERVICE_CLS = PreProcessing
    MOCKED_STREAMS_DICT = {
        PREPROCESSING_STREAM_KEY: [],
        PREPROCESSING_CMD_KEY: [],
        USER_MANAGER_STREAM_KEY: [],
    }

    @patch('preprocessing.service.PreProcessing._run_subprocess')
    def test_process_action_start_preprocessing_for_buffer_stream_call_sub_process(self, mocked_run_sub_process):
        event_msg_tuple = prepare_event_msg_tuple({
            'action': 'startPreprocessing',
            'source': 'source',
            'resolution': 'resolution',
            'fps': '15',
            'buffer_stream_key': 'buffer_stream_key',
        })
        self.service.service_stream.mocked_values = [event_msg_tuple]
        self.service.process_events()
        self.assertTrue(self.service._run_subprocess.called)

    def test_process_cmd_(self):
        pass

    def test_process_events_(self):
        pass
        self.assertEqual(True, True)
