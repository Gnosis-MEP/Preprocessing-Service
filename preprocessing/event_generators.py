import time
import uuid

import cv2
from PIL import Image
from minio import Minio

from event_service_utils.schemas.events import EventVEkgMessage

from event_service_utils.event_generators_processors.img_based import (
    BaseEventGenerator,
    MinioMixing
)

from preprocessing.ffmpeg_reader import FFMPEGReader


class ImageUploadFromRTMPEventGenerator(BaseEventGenerator, MinioMixing):
    def __init__(self, file_storage_cli_config, media_source, width, height, fps, source):
        self.file_storage_cli_config = file_storage_cli_config
        self.initialize_file_storage_client()
        self.media_source = media_source
        self.width = width
        self.height = height
        self.fps = fps
        self.reader = FFMPEGReader(
            source=media_source,
            width=self.width,
            height=self.height,
            fps=self.fps
        )
        # self.reader = cv2.VideoCapture(media_source)
        # self.reader.set(cv2.CAP_PROP_FPS, float(self.fps))

        BaseEventGenerator.__init__(
            self, source=source, event_schema=EventVEkgMessage)
        self._create_bucket_for_publisher()

    def initialize_file_storage_client(self):
        self.fs_client = Minio(
            **self.file_storage_cli_config
        )

    def next_event(self):
        try:
            if self.reader.isOpened():
                ret, frame = self.reader.read()
                # self.reader.grab()
                # ret, frame = self.reader.retrieve()
                while not ret:
                    # self.reader.grab()
                    # time.sleep(0.05)
                    ret, frame = self.reader.read()

                if ret:
                    cv2.imshow(f'{self.media_source}-{self.fps}', frame)
                    cv2.waitKey(1)
                    print("new frame")
                    pil_img = Image.fromarray(frame[:, :, ::-1].copy())

                    event_id = f'{self.source}-{str(uuid.uuid4())}'
                    obj_data = self.upload_inmemory_to_storage(pil_img)
                    # obj_data = ''
                    # print(obj_data)

                    img_url = obj_data
                    schema = self.event_schema(id=event_id, vekg={}, image_url=img_url, source=self.source)
                    return schema.json_msg_load_from_dict()
        except Exception as e:
            self.reader.close()
            raise e
        # finally:
