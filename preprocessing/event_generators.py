import functools
import logging

import time
import uuid

import numpy as np
import cv2
from PIL import Image

import logzero

from event_service_utils.schemas.events import EventVEkgMessage

from event_service_utils.event_generators_processors.base import BaseEventGenerator
from event_service_utils.img_serialization.redis import RedisImageCache
from event_service_utils.img_serialization.base import image_to_bytes

from preprocessing.ffmpeg_reader import FFMPEGReader, OCVBasedFFMPEGReader
from preprocessing.conf import LOGGING_LEVEL


def timer_logger(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        logger = args[0].logger
        logger.debug(f"Finished {func.__qualname__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer


def setup_logger(name):
    log_format = (
        '%(color)s[%(levelname)1.1s %(name)s %(asctime)s:%(msecs)d '
        '%(module)s:%(funcName)s:%(lineno)d]%(end_color)s %(message)s'
    )
    formatter = logzero.LogFormatter(fmt=log_format)
    return logzero.setup_logger(name=name, level=logging.getLevelName(LOGGING_LEVEL), formatter=formatter)


class ImageUploadFromRTMPEventGenerator(BaseEventGenerator, RedisImageCache):
    def __init__(self, file_storage_cli_config, source, media_source, width, height, fps, ffmpeg_bin):
        self.file_storage_cli_config = file_storage_cli_config
        self.initialize_file_storage_client()
        self.media_source = media_source
        self.width = width
        self.height = height
        self.fps = fps
        self.reader = FFMPEGReader(
            media_source=media_source,
            width=self.width,
            height=self.height,
            fps=self.fps,
            ffmpeg=ffmpeg_bin
        )
        self.color_channels = 'BGR'
        self.logger = setup_logger(self.__class__.__name__)

        BaseEventGenerator.__init__(
            self, source=source, event_schema=EventVEkgMessage)

    @timer_logger
    def upload_inmemory_to_storage(self, img_numpy_array):
        return super(ImageUploadFromRTMPEventGenerator, self).upload_inmemory_to_storage(img_numpy_array)

    @timer_logger
    def next_event(self):
        try:
            if self.reader.isOpened():
                ret, frame = self.reader.read()
                while not ret:
                    time.sleep(0.1)
                    ret, frame = self.reader.read()
                    print('bad ret')

                if ret:
                    # cv2.imshow(f'{self.media_source}-{self.fps}-{self.width}x{self.height}', frame)
                    # cv2.waitKey(1)
                    event_id = f'{self.source}-{str(uuid.uuid4())}'
                    obj_data = self.upload_inmemory_to_storage(frame)

                    img_url = obj_data
                    schema = self.event_schema(id=event_id, vekg={}, image_url=img_url, source=self.source)
                    schema.dict.update({
                        'width': self.width,
                        'height': self.height,
                        'color_channels': self.color_channels
                    })

                    msg_json = schema.json_msg_load_from_dict()
                    print(msg_json)
                    return msg_json
        except Exception as e:
            self.reader.close()
            raise e
