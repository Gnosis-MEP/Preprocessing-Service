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
        'logging_level': 'ERROR'
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
            'resolution': '640×480',
            'fps': '15',
            'buffer_stream_key': 'buffer_stream_key',
        })
        self.service.service_stream.mocked_values = [event_msg_tuple]
        self.service.process_events()
        self.assertTrue(self.service._run_subprocess.called)

    @patch('preprocessing.service.PreProcessing._run_subprocess')
    def test_process_action_stop_preprocessing_for_buffer_stream_kill_sub_process(self, mocked_run_sub_process):
        event_msg_tuple = prepare_event_msg_tuple({
            'action': 'startPreprocessing',
            'source': 'source',
            'resolution': '640×480',
            'fps': '15',
            'buffer_stream_key': 'buffer_stream_key',
        })
        self.service.service_stream.mocked_values = [event_msg_tuple]
        self.service.process_events()

        event_msg_tuple = prepare_event_msg_tuple({
            'action': 'stopPreprocessing',
            'buffer_stream_key': 'buffer_stream_key',
        })
        self.service.service_stream.mocked_values = [event_msg_tuple]
        self.service.process_events()
        self.assertEqual(1, len((mocked_run_sub_process.return_value.method_calls)))
        self.assertIn('kill', str(mocked_run_sub_process.return_value.method_calls[0]))

    @patch('preprocessing.service.PreProcessing.start_preprocessing_for_buffer_stream')
    def test_process_action_should_call_start_processing_with_right_args(self, start_proc_mock):
        event_msg_tuple = prepare_event_msg_tuple({
            'action': 'startPreprocessing',
            'source': 'source',
            'resolution': '640×480',
            'fps': '15',
            'buffer_stream_key': 'buffer_stream_key',
        })
        self.service.service_stream.mocked_values = [event_msg_tuple]
        self.service.process_events()

        start_proc_mock.assert_called_once_with('source', '640×480', '15', 'buffer_stream_key')

    def test_process_events_(self):
        pass
        self.assertEqual(True, True)
