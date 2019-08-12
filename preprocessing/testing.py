#
# Reading video from FFMPEG using subprocess - aka when OpenCV VideoCapture fails
#
# 2017 note: I have realized that this is similar to moviepy ffmpeg reader with the difference that here we support YUV encoding
# BUT we lack: bufsize in POpen and creation flags for windows
# https://github.com/Zulko/moviepy/blob/master/moviepy/video/io/ffmpeg_reader.py
#
# Emanuele Ruffaldi 2016
import cv2
import subprocess
import numpy as np
import os

class FFmpegVideoCapture:
    # TODO probe width/height
    # TODO enforce width/height
    #
    # mode=gray,yuv420p,rgb24,bgr24
    def __init__(self,source,width,height,mode="gray",start_seconds=0,duration=0,verbose=False):

        x = ['ffmpeg']
        if start_seconds > 0:
            #[-][HH:]MM:SS[.m...]
            #[-]S+[.m...]
            x.append("-accurate_seek")
            x.append("-ss")
            x.append("%f" % start_seconds)
        if duration > 0:
            x.append("-t")
            x.append("%f" % duration)
        x.extend(['-i', source,"-f","rawvideo", "-pix_fmt" ,mode,"-"])
        self.nulldev = open(os.devnull,"w") if not verbose else None
        self.ffmpeg = subprocess.Popen(x, stdout = subprocess.PIPE, stderr=subprocess.STDERR if verbose else self.nulldev)
        self.width = width
        self.height = height
        self.mode = mode
        if self.mode == "gray":
            self.fs = width*height
        elif self.mode == "yuv420p":
            self.fs = width*height*6/4
        elif self.mode == "rgb24" or self.mode == "bgr24":
            self.fs = width*height*3
        self.output = self.ffmpeg.stdout
    def read(self):
        if self.ffmpeg.poll():
            return False,None
        x = self.output.read(int(self.fs))
        if x == "":
            return False,None
        if self.mode == "gray":
            return True,np.frombuffer(x,dtype=np.uint8).reshape((self.height,self.width))
        elif self.mode == "yuv420p":
            # Y fullsize
            # U w/2 h/2
            # V w/2 h/2
            k = self.width*self.height
            return True,(np.frombuffer(x[0:k],dtype=np.uint8).reshape((self.height,self.width)),
                np.frombuffer(x[k:k+(k/4)],dtype=np.uint8).reshape((self.height/2,self.width/2)),
                np.frombuffer(x[k+(k/4):],dtype=np.uint8).reshape((self.height/2,self.width/2))
                    )
        elif self.mode == "bgr24" or self.mode == "rgb24":
            return True,(np.frombuffer(x,dtype=np.uint8).reshape((self.height,self.width,3)))


if __name__ == '__main__':
    import ipdb; ipdb.set_trace()
    import sys
    if len(sys.argv) < 5:
        print("filename w h mode\nWhere mode is: gray|yuv420p|bgr24")
    else:
        capture = FFmpegVideoCapture(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4])
        while True:
            ret, img = capture.read()
            if not ret:
                print( "exit with",ret,img)
                break
            if type(img) is tuple:
                cv2.imshow("Y",img[0])
                cv2.imshow("U",img[1])
                cv2.imshow("V",img[2])
            else:
                cv2.imshow("img",img)
            cv2.waitKey(1)