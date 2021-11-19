from unittest.mock import patch, MagicMock

from event_service_utils.tests.base_test_case import MockedEventDrivenServiceStreamTestCase
from event_service_utils.tests.json_msg_helper import prepare_event_msg_tuple

from preprocessing.service import PreProcessing

from preprocessing.conf import (
    SERVICE_STREAM_KEY,
    SERVICE_CMD_KEY_LIST,
    SERVICE_DETAILS,
    PUB_EVENT_LIST,
    RUN_STREAM_TO_BUFFERS,
)


class TestPreprocessing(MockedEventDrivenServiceStreamTestCase):
    GLOBAL_SERVICE_CONFIG = {
        'service_stream_key': SERVICE_STREAM_KEY,
        'service_cmd_key_list': SERVICE_CMD_KEY_LIST,
        'pub_event_list': PUB_EVENT_LIST,
        'service_details': SERVICE_DETAILS,
        'stream_to_buffers_bin': RUN_STREAM_TO_BUFFERS,
        'logging_level': 'ERROR',
        'tracer_configs': {'reporting_host': None, 'reporting_port': None},
    }
    SERVICE_CLS = PreProcessing

    MOCKED_CG_STREAM_DICT = {

    }
    MOCKED_STREAMS_DICT = {
        SERVICE_STREAM_KEY: [],
        'cg-PreProcessing': MOCKED_CG_STREAM_DICT,
    }

    @patch('preprocessing.service.PreProcessing.process_event_type')
    def test_process_cmd_should_call_process_event_type(self, mocked_process_event_type):
        event_type = 'SomeEventType'
        unicode_event_type = event_type.encode('utf-8')
        event_data = {
            'id': 1,
            'action': event_type,
            'some': 'stuff'
        }
        msg_tuple = prepare_event_msg_tuple(event_data)
        mocked_process_event_type.__name__ = 'process_event_type'

        self.service.service_cmd.mocked_values_dict = {
            unicode_event_type: [msg_tuple]
        }
        self.service.process_cmd()
        self.assertTrue(mocked_process_event_type.called)
        self.service.process_event_type.assert_called_once_with(event_type=event_type, event_data=event_data, json_msg=msg_tuple[1])

    @patch('preprocessing.service.PreProcessing.start_preprocessing_for_buffer_stream')
    def test_process_event_type_should_call_start_preprocessing_for_buffer_stream_with_correct_args(self, mocked_start_process):
        event_data = {
            'id': 1,
            'query_id': 'query-id',
            'buffer_stream': {
                'publisher_id': '44d7985a-e41e-4d02-a772-a8f7c1c69124',
                'source': 'source',
                'resolution': '640x480',
                'fps': '15',
                'buffer_stream_key': 'buffer_stream_key',
            },
        }
        event_type = 'QueryCreated'
        json_msg = prepare_event_msg_tuple(event_data)[1]
        self.service.process_event_type(event_type=event_type, event_data=event_data, json_msg=json_msg)
        mocked_start_process.assert_called_once_with(
            '44d7985a-e41e-4d02-a772-a8f7c1c69124',
            'source',
            '640x480',
            '15',
            'buffer_stream_key',
            ['query-id']
        )

    @patch('preprocessing.service.PreProcessing._run_subprocess')
    def test_start_preprocessing_for_buffer_stream_should_call_run_subprocess(self, mocked_sp):
        mocked_sp.return_value = 'sub_p'
        publisher_id = '44d7985a-e41e-4d02-a772-a8f7c1c69124'
        source = 'source'
        resolution = '640x480'
        fps = '15'
        buffer_stream_key = 'buffer_stream_key'
        query_ids = ['query-id']
        preprocessing_data = {
            'publisher_id': publisher_id,
            'source': source,
            'resolution': resolution,
            'fps': fps,
            'buffer_stream_key': buffer_stream_key,
            'query_ids': query_ids,
            'subprocess': 'sub_p',
        }

        self.service.start_preprocessing_for_buffer_stream(
            publisher_id,
            source,
            resolution,
            fps,
            buffer_stream_key,
            query_ids
        )
        mocked_sp.assert_called_once_with(
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
        self.assertDictEqual(self.service.buffers, {'buffer_stream_key': preprocessing_data})

    @patch('preprocessing.service.PreProcessing.stop_preprocessing_for_buffer_stream')
    def test_process_event_type_should_call_stop_preprocessing_for_buffer_stream_with_correct_args(self, mocked_stop_process):
        event_data = {
            'id': 1,
            'query_id': 'query-id',
            'buffer_stream': {
                'publisher_id': '44d7985a-e41e-4d02-a772-a8f7c1c69124',
                'source': 'source',
                'resolution': '640x480',
                'fps': '15',
                'buffer_stream_key': 'buffer_stream_key',
            },
            'deleted': True,
        }
        event_type = 'QueryRemoved'
        json_msg = prepare_event_msg_tuple(event_data)[1]
        self.service.process_event_type(event_type=event_type, event_data=event_data, json_msg=json_msg)
        mocked_stop_process.assert_called_once_with(
            'buffer_stream_key',
        )

    def test_stop_preprocessing_for_buffer_stream_should_call_kill_sub_process(self):
        buffer_stream_key = 'buffer_stream_key'
        subprocess = MagicMock()
        self.service.buffers[buffer_stream_key] = {'subprocess': subprocess}
        self.service.stop_preprocessing_for_buffer_stream(buffer_stream_key)
        self.assertTrue(subprocess.kill.called)
