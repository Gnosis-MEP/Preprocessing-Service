from unittest.mock import patch

from event_service_utils.tests.base_test_case import MockedServiceStreamTestCase
from event_service_utils.tests.json_msg_helper import prepare_event_msg_tuple

from preprocessing.service import PreProcessing

from preprocessing.conf import (
    SERVICE_STREAM_KEY,
    SERVICE_CMD_KEY,
    RUN_STREAM_TO_BUFFERS,
)


class TestPreprocessing(MockedServiceStreamTestCase):
    GLOBAL_SERVICE_CONFIG = {
        'service_stream_key': SERVICE_STREAM_KEY,
        'service_cmd_key': SERVICE_CMD_KEY,
        'stream_to_buffers_bin': RUN_STREAM_TO_BUFFERS,
        'logging_level': 'ERROR',
        'tracer_configs': {'reporting_host': None, 'reporting_port': None},
    }
    SERVICE_CLS = PreProcessing
    MOCKED_STREAMS_DICT = {
        SERVICE_STREAM_KEY: [],
        SERVICE_CMD_KEY: [],
    }

    @patch('preprocessing.service.PreProcessing.process_action')
    def test_process_cmd_should_call_process_action(self, mocked_process_action):
        action = 'someAction'
        event_data = {
            'id': '1',
            'action': action,
            'some': 'stuff'
        }
        msg_tuple = prepare_event_msg_tuple(event_data)
        mocked_process_action.__name__ = 'process_action'

        self.service.service_cmd.mocked_values = [msg_tuple]
        self.service.process_cmd()
        self.assertTrue(mocked_process_action.called)
        self.service.process_action.assert_called_once_with(action=action, event_data=event_data, json_msg=msg_tuple[1])

    @patch('preprocessing.service.PreProcessing._run_subprocess')
    def test_process_action_start_preprocessing_for_buffer_stream_call_sub_process(self, mocked_run_sub_process):
        event_msg_tuple = prepare_event_msg_tuple({
            'id': '1',
            'action': 'startPreprocessing',
            'publisher_id': '44d7985a-e41e-4d02-a772-a8f7c1c69124',
            'source': 'source',
            'resolution': '640x480',
            'fps': '15',
            'buffer_stream_key': 'buffer_stream_key',
            'query_id': 'query-id',
        })
        self.service.service_cmd.mocked_values = [event_msg_tuple]
        self.service.process_cmd()
        self.assertTrue(self.service._run_subprocess.called)
        self.service._run_subprocess.assert_called_once_with(
            [
                'python',
                self.GLOBAL_SERVICE_CONFIG['stream_to_buffers_bin'],
                '44d7985a-e41e-4d02-a772-a8f7c1c69124',
                'source',
                '640',
                '480',
                '15',
                'buffer_stream_key',
                'query-id'
            ]
        )

    @patch('preprocessing.service.PreProcessing._run_subprocess')
    def test_process_action_stop_preprocessing_for_buffer_stream_kill_sub_process(self, mocked_run_sub_process):
        event_msg_tuple = prepare_event_msg_tuple({
            'id': '1',
            'action': 'startPreprocessing',
            'publisher_id': '44d7985a-e41e-4d02-a772-a8f7c1c69124',
            'source': 'source',
            'resolution': '640x480',
            'fps': '15',
            'buffer_stream_key': 'buffer_stream_key',
        })
        self.service.service_cmd.mocked_values = [event_msg_tuple]
        self.service.process_cmd()

        event_msg_tuple = prepare_event_msg_tuple({
            'id': '2',
            'action': 'stopPreprocessing',
            'buffer_stream_key': 'buffer_stream_key',
        })
        self.service.service_cmd.mocked_values = [event_msg_tuple]
        self.service.process_cmd()
        self.assertEqual(1, len((mocked_run_sub_process.return_value.method_calls)))
        self.assertIn('kill', str(mocked_run_sub_process.return_value.method_calls[0]))

    @patch('preprocessing.service.PreProcessing.start_preprocessing_for_buffer_stream')
    def test_process_action_should_call_start_processing_with_right_args(self, start_proc_mock):
        event_msg_tuple = prepare_event_msg_tuple({
            'id': '1',
            'action': 'startPreprocessing',
            'publisher_id': '44d7985a-e41e-4d02-a772-a8f7c1c69124',
            'source': 'source',
            'resolution': '640x480',
            'fps': '15',
            'buffer_stream_key': 'buffer_stream_key',
            'query_id': 'query-id',
        })
        self.service.service_cmd.mocked_values = [event_msg_tuple]
        self.service.process_cmd()
        start_proc_mock.assert_called_once_with(
            '44d7985a-e41e-4d02-a772-a8f7c1c69124', 'source', '640x480', '15', 'buffer_stream_key', 'query_id')
