from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from plyer import filechooser
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import cv2
import tensorflow as tf
import cv2
from Ped_Detect_SSDLite import Ped_BBox_Module as pedMod
#from matplotlib import pyplot as plt
import time

Builder.load_string('''
<MainScreen>:
    rows: 3
    cols: 1
    padding: 5
    spacing: 5
    
    Image:
        id: prev
        source:'./assets/AutoCar.jpg'           
        size: root.size
    Button:
        text: 'Input a video (.mp4)'
        font_size: "20sp"
        background_color: (1, 1, 20, 1)
        color:(1, 1, 1, 1)
        size:(10, 12)
        size_hint:(.3, .1)        
        pos: (200, 90)
        on_press: root.InputVDRec()
    Button:
        text: 'Real Time Recognition! (Web Cam)'
        font_size: "20sp"
        background_color: (1, 0, 20 , 1)
        color:(1, 10, 1, 1)
        size:(10, 12)
        size_hint:(.2, .1)
        pos: (200, 70)
        on_press: root.RealTimeRec()
''')

class MainScreen(GridLayout):
    RealTime = False
    Time = True

    def InputVDRec(self):
        MainScreen.RealTime = False
        try:
            path = filechooser.open_file(title="Select a Video File", filters=[("Video File", "*.mp4")])
            self.capture = cv2.VideoCapture(path[0])
            Clock.schedule_interval(self.update, 1.0 / 60)
        except Exception as e:
            print("Exception")
        return

    def RealTimeRec(self):
        MainScreen.RealTime = True
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 60)

    def update(self, *args):
        try:
            ret, frame = self.capture.read()
            if ret:
                if MainScreen.RealTime:
                    frame=cv2.flip(frame,2)

                bbox_list = pedMod.get_person_bbox(frame, thr=0.6)
                cur=int(time.time())
                if bbox_list and (self.Time == 1 or cur > self.Time+10):
                    self.Time = cur
                    Ped_detect = SoundLoader.load(r'C:\Users\Sanjay-PC\PycharmProjects\PedestrianDetectionApp\assets\Ped_Detected-speech.mp3')
                    if Ped_detect:
                        Ped_detect.play()
                        self.Ins= False

                for i in bbox_list:
                    cv2.rectangle(frame, i[0], i[1], (125, 255, 51), thickness=5)
                    cv2.putText(frame, text="Pedestrian", org=i[0], fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale=1, color=(36, 255, 12), thickness=2)

                self.ids.prev.image_frame = frame
                buffer = cv2.flip(self.ids.prev.image_frame, 0).tobytes()

                texture = Texture.create(size=(self.ids.prev.image_frame.shape[1], self.ids.prev.image_frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
                # Change the texture of the instance
                self.ids.prev.texture = texture
            else:
                pass 
        except Exception as e:
            print(e)
            pass
        return

class PedestrianDetectionApp(App):
    def build(self):
        intro_sound = SoundLoader.load('assets/ADAS_Intro.mp3')
        if intro_sound:
            intro_sound.play()

        return MainScreen()

if __name__ == '__main__':
    PedestrianDetectionApp().run()