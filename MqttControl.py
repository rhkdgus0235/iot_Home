from gpiozero import PWMLED,AngularServo
import threading
from homeiot_final import analog_sensor_shade
import cv2
from Record import Record
red=PWMLED(16)
green=PWMLED(13)
blue=PWMLED(26)
record=Record()
angle_blind=AngularServo(19, min_angle=-90, max_angle=90, min_pulse_width=0.0004, max_pulse_width=0.0024)
angle_camera=AngularServo(23, min_angle=-90, max_angle=90, min_pulse_width=0.0004, max_pulse_width=0.0024)
class MqttControl:
    def __init__(self) -> None:
        
        self.living_true=0
        self.kitchen_true=0
        self.mainroom_true=0
        self.automode_true=0

        listI=[]
        for i in range(0,101):
            listI.append(i)

        self.listS=list(map(str,listI))

    def on_connect(self,client,userdata,flags,rc):
        print("Connected with result code"+str(rc))
        if rc==0:
            client.subscribe("iot/#")
        else:
            print('연결실패:',rc)


    def on_message(self,client,userdata,msg):
        # global living_true,kitchen_true,mainroom_true, thread_state,automode_true,shade_state
        print(msg.topic)
        mt=msg.topic
        
        value=msg.payload.decode()
        if (mt=="iot/led/livingroom" or mt=="iot/led/kitchen" or mt=="iot/led/mainroom"):
            if (mt=="iot/led/livingroom" and value=="on"):
                print('거실led를 키겠습니다')
                
                self.living_true=1
                red.value=0.5
                
            elif(mt=="iot/led/livingroom" and value=="off"):
                print("거실led를 끄겠습니다")
                self.living_true=0
                red.off()
            elif(mt=="iot/led/kitchen" and value=="on"):
                print("주방led를 키겠습니다")
                self.kitchen_true=1
                green.value=0.5
            elif(mt=="iot/led/kitchen" and value=="off"):
                print("주방led를 끄겠습니다")
                self.kitchen_true=0
                green.off()
            elif(mt=="iot/led/mainroom" and value=="on"):
                print("안방led를 끄겠습니다")
                self.mainroom_true=1
                blue.value=0.5
            elif(mt=="iot/led/mainroom" and value=="off"):
                print("안방led를 끄겠습니다")
                self.mainroom_true=0
                blue.off()
            elif(self.living_true==1 and mt=="iot/led/livingroom"):
                
                if (value in self.listS):
                    print(self.living_true)
                    print(float(int(value)/100))
                    red.value=float(int(value)/100)
            elif(self.kitchen_true==1 and mt=="iot/led/kitchen"):
                
                if (value in self.listS):
                    print(self.kitchen_true)
                    print(float(int(value)/100))
                    green.value=float(int(value)/100)
            
            elif(self.mainroom_true==1 and mt=="iot/led/mainroom"):
                
                if (value in self.listS):
                    print(self.mainroom_true)
                    print(float(int(value)/100))
                    blue.value=float(int(value)/100)



            # print(f"{float(value)}")  #카메라각도값 제어
            print(f"{msg.topic} {value}")
        
        else:
            if(msg.topic=="iot/blind" and value=="automode_on" ):
                automode_true=1
                shade_state=True
                print(shade_state)
                count=0
                if (automode_true==1 and shade_state==True):
                    if count==0:
                        shades_thread=threading.Thread(target=analog_sensor_shade,args=())
                        shades_thread.start()
                        count+=1

            elif(msg.topic=="iot/blind" and value=="automode_off"):
                automode_true=0
                shade_state=False
                
                print(shade_state)
            elif(msg.topic=="iot/camera/angle"):
                print("카메라각 제어")
                angle_camera.angle=float(value)
                print(f"{msg.topic} {value}")
            elif(msg.topic=="iot/camera/capture" and value=="captured"):
                print("내부카메라 캡쳐 ")
                cap=cv2.VideoCapture(1)
        
        

        
                retval, frame=cap.read()  

                # os.system("fswebcam --device /dev/video1 image.jpeg")
                cv2.imwrite('messigray.png',frame, params=[cv2.IMWRITE_PNG_COMPRESSION,0])
            elif(msg.topic=="iot/camera/record" and value=="on"):
                
                print("내부카메라 녹화")
                t_record=threading.Thread(target=record.record_thread,args=())
                t_record.start()
                
                # cv2.imshow('frame',frame)

                
            elif (msg.topic=="iot/camera/record" and value=="off"):
                print("내부카메라 녹화종료")
                # t_record=threading.Thread(target=record_thread,args=(1,))
                # t_record.start()
                thread_state = False
            elif (automode_true==0 and mt=="iot/blind"):
                if (value in self.listS):
                    print("블라각 제어")
                    angle_blind.angle=float(value)
                    print(f"{msg.topic} {value}")
            # elif (automode_true==1 and shade_state==True):
            #     count=0
            #     if count==0:

                    # shades_thread=threading.Thread(target=analog_sensor_shade,args=())
                    # shades_thread.start()
                    # count+=1


# 테스트파일