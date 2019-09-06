import functools
import logging

import time
import uuid

import numpy as np
import cv2
from PIL import Image

import logzero

from event_service_utils.event_generators_processors.base import BaseEventGenerator
from event_service_utils.img_serialization.redis import RedisImageCache
from event_service_utils.img_serialization.base import image_to_bytes

from preprocessing.ffmpeg_reader import FFMPEGReader, OCVBasedFFMPEGReader
from preprocessing.schemas import EventVEkgMessage
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
    def __init__(
            self, file_storage_cli_config, publisher_id, media_source, width, height, fps, ffmpeg_bin, expiration_time):
        self.file_storage_cli_config = file_storage_cli_config
        self.initialize_file_storage_client()
        self.publisher_id = publisher_id
        self.media_source = media_source
        self.width = width
        self.height = height
        self.fps = fps
        self.expiration_time = expiration_time
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
            self, source=publisher_id, event_schema=EventVEkgMessage)

    @timer_logger
    def upload_inmemory_to_storage(self, img_numpy_array):
        img_key = str(uuid.uuid4())
        nd_array_bytes = img_numpy_array.tobytes(order='C')

        ret = self.client.set(img_key, nd_array_bytes)
        if ret:
            self.client.expire(img_key, self.expiration_time)
        else:
            raise Exception('Couldnt set image in redis')
        return img_key

    @timer_logger
    def next_event(self):
        try:
            if self.reader.isOpened():
                ret, frame = self.reader.read()
                while not ret:
                    self.logger.error(f'Bad return reading frame from {self.reader}, will sleep a bit and try again')
                    time.sleep(0.1)
                    ret, frame = self.reader.read()

                if ret:
                    # cv2.imshow(f'{self.media_source}-{self.fps}-{self.width}x{self.height}', frame)
                    # cv2.waitKey(1)
                    event_id = f'{self.source}-{str(uuid.uuid4())}'
                    obj_data = self.upload_inmemory_to_storage(frame)

                    img_url = obj_data
                    schema = self.event_schema(
                        id=event_id, vekg={}, image_url=img_url,
                        publisher_id=self.publisher_id, source=self.media_source
                    )
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
