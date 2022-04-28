import cv2
from datetime import datetime
from time import sleep
class Record:
    def __init__(self):
        self.frame_size = (640,480)

        self.fourcc=cv2.VideoWriter_fourcc(*'mp4v')
        self.writer=None
        self.thread_state = False

    def start_record(self):
        # global writer, thread_state
        if self.writer: return
        self.thread_state = True
        start=datetime.now()
        fname=start.strftime('./data/%Y%m%d_%H%M%S.mp4')
        self.writer=cv2.VideoWriter(fname,self.fourcc,20.0,self.frame_size)
        print('frame_size = ', self.frame_size)

    def stop_record(self):
        # global writer, thread_state
        if not self.writer:return

        self.writer.release()
        self.writer=None
        print('stop recording')

    def record_thread(self):
        cap=cv2.VideoCapture(1)
        self.start_record()
        print("카메라 상태", cap.isOpened())

        while self.thread_state:
            retval, frame=cap.read()        
            if self.writer:
                print(retval)
                self.writer.write(frame)
            else:
                self.print("writer 없음")

        self.stop_record()
        sleep(2)