#!/usr/bin/python3
import time
import os
from picamera2 import Picamera2, Preview
from picamera2.encoders import JpegEncoder

stop_ext_trig_cmd = 'v4l2-ctl -d /dev/v4l-subdev0 -c trigger_mode=0'
os.system(stop_ext_trig_cmd)

picam2 = Picamera2()

video_config = picam2.create_video_configuration(main={"size": (5120, 800)}, lores={"size": (4096, 800)}, display="lores",buffer_count=10)
picam2.configure(video_config)

picam2.start_preview(Preview.QTGL)

encoder = JpegEncoder(q=70)
picam2.start_recording(encoder, 'dummy.mjpeg')
# config = picam2.create_preview_configuration()
# picam2.configure(config)

# picam2.start_preview(Preview.DRM)

time.sleep(1000)

picam2.stop_preview()
# picam2.start_preview(True)
# 
# time.sleep(2)