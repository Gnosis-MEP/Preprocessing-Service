import os

from decouple import config

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SOURCE_DIR)

RUN_STREAM_TO_BUFFERS = os.path.join(SOURCE_DIR, 'run_stream_to_buffer.py')

REDIS_ADDRESS = config('REDIS_ADDRESS', default='localhost')
REDIS_PORT = config('REDIS_PORT', default='6379')

SERVICE_STREAM_KEY = config('SERVICE_STREAM_KEY', default='pp-data')
SERVICE_CMD_KEY = config('SERVICE_CMD_KEY', default='pp-cmd')

LOGGING_LEVEL = config('LOGGING_LEVEL', default='ERROR')

FFMPEG_BIN = config('FFMPEG_BIN', default='ffmpeg')
