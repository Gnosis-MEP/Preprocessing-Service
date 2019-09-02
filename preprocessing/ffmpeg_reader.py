import time
import subprocess
import numpy

import cv2

# https://stackoverflow.com/questions/35166111/opencv-python-reading-video-from-named-pipe


class FFMPEGReader():
    """docstring for FFMPEGReader"""

    def __init__(self, media_source, width, height, fps, ffmpeg='ffmpeg'):
        super(FFMPEGReader, self).__init__()
        self.ffmpeg = ffmpeg
        self.media_source = media_source
        self.width = width
        self.height = height
        self.fps = fps
        self.cmd = self.prepare_cmd()
        self.bufsize = 10**8
        self.subprocess = self.open_subprocess_pipe(self.cmd)

    def prepare_cmd(self):
        command = [
            self.ffmpeg,
            '-i', self.media_source,
            '-pix_fmt', 'bgr24',      # opencv requires bgr24 pixel format.
            '-vcodec', 'rawvideo',
            '-r', f'{self.fps}',
            '-s', f'{self.width}x{self.height}',
            '-an', '-sn',              # we want to disable audio processing (there is no audio)
            '-f', 'image2pipe', '-'
        ]
        return command

    def open_subprocess_pipe(self, cmd):
        pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=self.bufsize)
        return pipe

    def read(self):
        raw_image = self.subprocess.stdout.read(self.width * self.height * 3)
        self.subprocess.stdout.flush()
        # transform the byte read into a numpy array
        image = numpy.fromstring(raw_image, dtype='uint8')
        image = image.reshape((self.height, self.width, 3))
        if image is None:
            return False, []
        return True, image

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
        self.capture = cv2.VideoCapture(0)

    def prepare_cmd(self):
        command = [
            self.ffmpeg,
            '-f', 'video4linux2',
            '-i', self.media_source,
            '-c:v', 'libx264',
            '-f', 'flv',
            '-r', f'{self.fps}',
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
