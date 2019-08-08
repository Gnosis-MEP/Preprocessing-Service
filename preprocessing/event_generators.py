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


class ImageUploadFromRTMPEventGenerator(BaseEventGenerator, MinioMixing):
    def __init__(self, file_storage_cli_config, media_source, source, frame_skip_n=0):
        self.file_storage_cli_config = file_storage_cli_config
        self.initialize_file_storage_client()
        self.media_source = media_source
        self.reader = cv2.VideoCapture(media_source)
        self.frame_skip_n = frame_skip_n

        BaseEventGenerator.__init__(
            self, source=source, event_schema=EventVEkgMessage)
        self._create_bucket_for_publisher()

    def initialize_file_storage_client(self):
        self.fs_client = Minio(
            **self.file_storage_cli_config
        )

    def next_event(self):
        if self.reader.isOpened():
            for i in range(self.frame_skip_n + 1):
                self.reader.grab()
            ret, frame = self.reader.retrieve()
            if ret:
                cv2.imshow(f'{self.media_source}-{self.frame_skip_n}', frame)
                cv2.waitKey(1)
                pil_img = Image.fromarray(frame[:, :, ::-1].copy())

                event_id = f'{self.source}-{str(uuid.uuid4())}'
                obj_data = self.upload_inmemory_to_storage(pil_img)
                # print(obj_data)

                img_url = obj_data
                schema = self.event_schema(id=event_id, vekg={}, image_url=img_url, source=self.source)
                return schema.json_msg_load_from_dict()
