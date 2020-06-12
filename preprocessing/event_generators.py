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
from event_service_utils.logging.decorators import timer_logger

from preprocessing.ffmpeg_reader import FFMPEGReader, OCVBasedFFMPEGReader, OCVLocalImagesReader
from preprocessing.schemas import EventVEkgMessage
from preprocessing.conf import LOGGING_LEVEL


def setup_logger(name):
    log_format = (
        '%(color)s[%(levelname)1.1s %(name)s %(asctime)s:%(msecs)d '
        '%(module)s:%(funcName)s:%(lineno)d]%(end_color)s %(message)s'
    )
    formatter = logzero.LogFormatter(fmt=log_format)
    return logzero.setup_logger(name=name, level=logging.getLevelName(LOGGING_LEVEL), formatter=formatter)


class ImageUploadFromRTMPEventGenerator(BaseEventGenerator, RedisImageCache):
    def __init__(
            self, file_storage_cli_config, publisher_id, media_source, width, height, fps, query_ids, ffmpeg_bin, expiration_time):
        self.file_storage_cli_config = file_storage_cli_config
        self.initialize_file_storage_client()
        self.publisher_id = publisher_id
        self.media_source = media_source
        self.width = width
        self.height = height
        self.fps = fps
        self.query_ids = query_ids
        self.expiration_time = expiration_time
        self.color_channels = 'BGR'
        self.logger = setup_logger(self.__class__.__name__)
        self.reader = FFMPEGReader(
            media_source=media_source,
            width=self.width,
            height=self.height,
            fps=self.fps,
            logger=self.logger,
            ffmpeg=ffmpeg_bin
        )

        BaseEventGenerator.__init__(
            self, source=publisher_id, event_schema=EventVEkgMessage)

    @timer_logger
    def upload_inmemory_to_storage(self, img_numpy_array):
        return super(ImageUploadFromRTMPEventGenerator, self).upload_inmemory_to_storage(img_numpy_array)

    def next_event(self):
        try:
            schema = None
            return_flag, frame = self.reader.read()
            if not return_flag:
                self.logger.error(f'Bad return reading frame from {self.reader} retrying for next one.' )
            if return_flag:
                # cv2.imshow(f'{self.media_source}-{self.fps}-{self.width}x{self.height}', frame)
                # cv2.waitKey(1)
                event_id = f'{self.source}-{str(uuid.uuid4())}'
                obj_data = self.upload_inmemory_to_storage(frame)

                img_url = obj_data
                schema = self.event_schema(
                    id=event_id, vekg={}, image_url=img_url,
                    publisher_id=self.publisher_id, source=self.media_source,
                    query_ids=self.query_ids
                )
                schema.dict.update({
                    'width': self.width,
                    'height': self.height,
                    'color_channels': self.color_channels
                })
            return schema
        except Exception as e:
            self.reader.close()
            raise e


class ImageUploadFromLocalImagesEventGenerator(BaseEventGenerator, RedisImageCache):
    def __init__(
            self, file_storage_cli_config, publisher_id, images_dir, width, height, fps, query_ids, expiration_time):
        self.file_storage_cli_config = file_storage_cli_config
        self.initialize_file_storage_client()
        self.publisher_id = publisher_id
        self.images_dir = images_dir
        self.width = width
        self.height = height
        self.fps = fps
        self.query_ids = query_ids
        self.expiration_time = expiration_time
        self.color_channels = 'BGR'
        self.logger = setup_logger(self.__class__.__name__)
        self.reader = OCVLocalImagesReader(
            images_dir=self.images_dir,
            width=self.width,
            height=self.height,
            fps=self.fps
        )

        BaseEventGenerator.__init__(
            self, source=publisher_id, event_schema=EventVEkgMessage)

    @timer_logger
    def upload_inmemory_to_storage(self, img_numpy_array):
        return super(ImageUploadFromLocalImagesEventGenerator, self).upload_inmemory_to_storage(img_numpy_array)

    def next_event(self):
        try:
            schema = None
            return_flag, frame = self.reader.read()
            if not return_flag:
                self.logger.error(f'Bad return reading frame from {self.reader} retrying for next one.' )
                raise Exception('Finished all images')
            if return_flag:
                event_id = f'{self.source}-{str(uuid.uuid4())}'
                obj_data = self.upload_inmemory_to_storage(frame)
                # cv2.imshow(f'{self.images_dir}-{self.fps}-{self.width}x{self.height}', frame)
                # cv2.waitKey(1)

                # saved_image = self.get_image_ndarray_by_key_and_shape(obj_data, (self.height, self.width, 3))

                img_url = obj_data
                schema = self.event_schema(
                    id=event_id, vekg={}, image_url=img_url,
                    publisher_id=self.publisher_id, source=self.images_dir,
                    query_ids=self.query_ids
                )
                schema.dict.update({
                    'width': self.width,
                    'height': self.height,
                    'color_channels': self.color_channels
                })
            return schema
        except Exception as e:
            self.reader.close()
            raise e
