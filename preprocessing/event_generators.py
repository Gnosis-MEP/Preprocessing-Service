import time
import uuid

import cv2
from PIL import Image

from event_service_utils.schemas.events import EventVEkgMessage

from event_service_utils.event_generators_processors.base import BaseEventGenerator
from event_service_utils.img_serialization.redis import RedisImageCache

from preprocessing.ffmpeg_reader import FFMPEGReader, OCVBasedFFMPEGReader


class ImageUploadFromRTMPEventGenerator(BaseEventGenerator, RedisImageCache):
    def __init__(self, file_storage_cli_config, source, media_source, width, height, fps, ffmpeg_bin):
        self.file_storage_cli_config = file_storage_cli_config
        self.initialize_file_storage_client()
        self.media_source = media_source
        self.width = width
        self.height = height
        self.fps = fps
        self.reader = OCVBasedFFMPEGReader(
            media_source=media_source,
            width=self.width,
            height=self.height,
            fps=self.fps,
            ffmpeg=ffmpeg_bin
        )

        BaseEventGenerator.__init__(
            self, source=source, event_schema=EventVEkgMessage)

    def next_event(self):
        try:
            if self.reader.isOpened():
                ret, frame = self.reader.read()
                while not ret:
                    time.sleep(0.01)
                    ret, frame = self.reader.read()
                    print('bad ret')

                if ret:
                    cv2.imshow(f'{self.media_source}-{self.fps}-{self.width}x{self.height}', frame)
                    cv2.waitKey(1)
                    print("new frame")
                    pil_img = Image.fromarray(frame[:, :, ::-1].copy())

                    event_id = f'{self.source}-{str(uuid.uuid4())}'
                    obj_data = self.upload_inmemory_to_storage(pil_img)
                    img_url = obj_data
                    schema = self.event_schema(id=event_id, vekg={}, image_url=img_url, source=self.source)
                    msg_json = schema.json_msg_load_from_dict()
                    print(msg_json)

                    return msg_json
        except Exception as e:
            self.reader.close()
            raise e
