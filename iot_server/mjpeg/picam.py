import io
import time
import numpy as np
from picamera import PiCamera
from haardetect import Haardetect
import cv2

cascade_file='haarcascade_frontalface_alt.xml'
detector=Haardetect(cascade_file)

class PiCam:
    def __init__(self,framerate=25,width=640,height=480):
        self.size=(width,height)
        self.framerate=framerate

        self.camera=PiCamera()
        self.camera.resolution=self.size
        self.camera.framerate=self.framerate

    def snapshot(self):
        frame=io.BytesIO()
        self.camera.capture(frame,'jpeg',use_video_port=True)
        frame.seek(0)
        return frame.getvalue()

class MJpegStreamCam(PiCam):
    def __init__(self,framerate=25,width=640,height=480):
        super().__init__(framerate=framerate,width=width,height=height)

    def __iter__(self):
        frame=io.BytesIO()
        while True:
            self.camera.capture(frame,format='jpeg',use_video_port=True)
            image=frame.getvalue()
            yield (b'--myboundary\n'
                   b'Content-Type:image/jpeg\n'
                   b'Content-Length: '+f"{len(image)}".encode()+b'\n'
                   b'\n'+image+b'\n')

            image_conv=cv2.imdecode(image,cv2.IMREAD_COLOR)
            face_list=detector.detect(image_conv)
            if len(face_list)>0:
                detector.draw_rect(image_conv,face_list)
            # print(type(image))
            frame.seek(0)
            frame.truncate()