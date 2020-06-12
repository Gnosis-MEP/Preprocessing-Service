import os

from decouple import config

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SOURCE_DIR)

RUN_STREAM_TO_BUFFER_SCRIPT = config('RUN_STREAM_TO_BUFFER_SCRIPT', default='run_stream_to_buffer.py')
RUN_STREAM_TO_BUFFERS = os.path.join(SOURCE_DIR, RUN_STREAM_TO_BUFFER_SCRIPT)

REDIS_ADDRESS = config('REDIS_ADDRESS', default='localhost')
REDIS_PORT = config('REDIS_PORT', default='6379')

TRACER_REPORTING_HOST = config('TRACER_REPORTING_HOST', default='localhost')
TRACER_REPORTING_PORT = config('TRACER_REPORTING_PORT', default='6831')

SERVICE_STREAM_KEY = config('SERVICE_STREAM_KEY', default='pp-data')
SERVICE_CMD_KEY = config('SERVICE_CMD_KEY', default='pp-cmd')

LOGGING_LEVEL = config('LOGGING_LEVEL', default='ERROR')

FFMPEG_BIN = config('FFMPEG_BIN', default='ffmpeg')

REDIS_EXPIRATION_TIME = config('REDIS_EXPIRATION_TIME', default=30)
