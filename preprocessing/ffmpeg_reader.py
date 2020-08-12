import datetime
import glob
import os
import subprocess
import time

import numpy

import cv2

# https://stackoverflow.com/questions/35166111/opencv-python-reading-video-from-named-pipe


class FFMPEGReader():
    """docstring for FFMPEGReader"""

    def __init__(self, media_source, width, height, fps, logger, ffmpeg='ffmpeg'):
        super(FFMPEGReader, self).__init__()
        self.ffmpeg = ffmpeg
        self.media_source = media_source
        self.width = width
        self.height = height
        self.fps = fps
        self.logger = logger
        self.cmd = self.prepare_cmd()
        self.bufsize = 10**8
        self.current_frame_index = -1
        self.subprocess = self.open_subprocess_pipe(self.cmd)

    def prepare_cmd(self):
        command = [
            self.ffmpeg,
            # '-analyzeduration', '17777', '-probesize', '32',
            # '-fflags', 'nobuffer',
            '-r', f'{self.fps}',
            '-i', self.media_source,
            '-pix_fmt', 'bgr24',      # opencv requires bgr24 pixel format.
            '-vcodec', 'rawvideo',
            '-s', f'{self.width}x{self.height}',
            '-an', '-sn',              # we want to disable audio processing (there is no audio)
            '-f', 'image2pipe', '-'
        ]
        return command

    def open_subprocess_pipe(self, cmd):
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=self.bufsize)

    def read(self):
        raw_image = self.subprocess.stdout.read(self.width * self.height * 3)
        self.subprocess.stdout.flush()
        # transform the byte read into a numpy array
        image = numpy.fromstring(raw_image, dtype='uint8')
        if image.size == 0:
            return False, None
        else:
            self.current_frame_index += 1
            return True, image.reshape((self.height, self.width, 3))

    def isOpened(self):
        return self.subprocess.poll() is None

    def close(self):
        self.subprocess.kill()


class OCVBasedFFMPEGReader():
    """docstring for OCVBasedFFMPEGReader"""

    def __init__(self, media_source, width, height, fps, ffmpeg='ffmpeg'):
        super(OCVBasedFFMPEGReader, self).__init__()
        self.ffmpeg = ffmpeg
        self.media_source = media_source
        self.width = width
        self.height = height
        self.fps = fps
        self.cmd = self.prepare_cmd()
        # self.subprocess = self.open_subprocess_pipe(self.cmd)
        time.sleep(2)
        self.capture = cv2.VideoCapture('fifo')

    def prepare_cmd(self):
        command = [
            self.ffmpeg,
            '-r', f'{self.fps}',
            '-f', 'video4linux2',
            '-i', self.media_source,
            '-c:v', 'libx264',
            '-f', 'flv',
            '-s', f'{self.width}x{self.height}',
            '-an', '-sn',              # we want to disable audio processing (there is no audio)
            '-f', 'pipe:1', '>', 'fifo'
        ]
        return command

    def open_subprocess_pipe(self, cmd):
        pipe = subprocess.Popen(cmd)
        return pipe

    def read(self):
        # raw_image = self.subprocess.stdout.read(self.width * self.height * 3)
        return self.capture.read()
        # self.subprocess.stdout.flush()
        # # transform the byte read into a numpy array
        # image = numpy.fromstring(raw_image, dtype='uint8')
        # image = image.reshape((self.height, self.width, 3))
        # if image is None:
        #     return False, []
        # return True, image

    def isOpened(self):
        return self.capture.isOpened()
        # has_process = self.subprocess.poll() is None
        # return has_process and self.capture.isOpened()

    def close(self):
        self.capture.release()
        # self.subprocess.kill()


class OCVLocalImagesReader():
    """docstring for OCVBasedFFMPEGReader"""

    def __init__(self, images_dir, width, height, fps):
        super(OCVLocalImagesReader, self).__init__()
        self.images_dir = images_dir
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_time = 1 / fps
        self.images_abs_paths = self.get_images_paths()
        self.next_image_index = 0
        self.last_read_timestamp = datetime.datetime.now().timestamp()

    def sleep_remaining_sleep_for_fps(self):
        current_timestamp = datetime.datetime.now().timestamp()
        secs_since_last_read = current_timestamp - self.last_read_timestamp
        missing_sleep_time = self.frame_time - secs_since_last_read
        if missing_sleep_time > 0:
            time.sleep(missing_sleep_time)
        else:
            missing_sleep_time = 0

        self.last_read_timestamp = current_timestamp + missing_sleep_time

    def get_images_paths(self):
        images_abs_paths = []
        images_dir_extensions = os.path.join(self.images_dir, '*.jpg')
        for image_file in glob.glob(images_dir_extensions):
            images_abs_paths.append(image_file)
        return images_abs_paths

    def read(self):
        if not self.isOpened():
            return False, []
        next_image_path = self.images_abs_paths[self.next_image_index]
        next_image = cv2.imread(next_image_path)
        resized_image = cv2.resize(
            next_image, (self.height, self.width), interpolation=cv2.INTER_CUBIC)
        self.next_image_index += 1
        self.sleep_remaining_sleep_for_fps()
        return True, resized_image

    def isOpened(self):
        return self.next_image_index < len(self.images_abs_paths)

    def close(self):
        self.next_image_index = len(self.images_abs_paths)
