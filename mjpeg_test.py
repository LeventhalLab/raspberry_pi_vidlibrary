#!/usr/bin/python3
import time
import os
from datetime import datetime
from picamera2 import Picamera2, Preview
from picamera2.encoders import JpegEncoder

def create_vid_name(rat_num, task='pavlovian', parent_folder='/home/levlab/data', vid_type='.mjpeg'):
    
    if vid_type[0] != '.':
        vid_type = '.' + vid_type
        
    rat_ID = 'R{:04d}'.format(rat_num)
    vid_datetime = datetime.now()
    
    session_datestr = vid_datetime.strftime('%Y%m%d')
    session_name = '_'.join([rat_ID, session_datestr])
    
    vid_dtstr = vid_datetime.strftime('%Y%m%d_%H-%m-%S')
    vid_name = '_'.join([rat_ID, vid_dtstr, task]) + vid_type
    
    rat_path = os.path.join(parent_folder, rat_ID)
    session_path = os.path.join(rat_path, session_name)
    
    if not os.path.exists(session_path):
        os.makedirs(session_path)
        
    full_vid_name = os.path.join(session_path, vid_name)
    
    return full_vid_name


def create_ts_name(rat_num, task='pavlovian', parent_folder='/home/levlab/data'):
        
    rat_ID = 'R{:04d}'.format(rat_num)
    vid_datetime = datetime.now()
    
    session_datestr = vid_datetime.strftime('%Y%m%d')
    session_name = '_'.join([rat_ID, session_datestr])
    
    vid_dtstr = vid_datetime.strftime('%Y%m%d_%H-%m-%S')
    ts_name = '_'.join([rat_ID, vid_dtstr, task, 'timestamps.txt'])
    
    rat_path = os.path.join(parent_folder, rat_ID)
    session_path = os.path.join(rat_path, session_name)
    
    if not os.path.exists(session_path):
        os.makedirs(session_path)
        
    full_ts_name = os.path.join(session_path, ts_name)
    
    return full_ts_name


def record_calibration_video(picam2, vid_name, ts_name, duration=5, fps=25):
    
    fdl = int(1000000 / fps)
    
    video_config = picam2.create_video_configuration(main={"size": (5120, 800)}, lores={"size": (320, 64)}, display="lores", controls={"FrameDurationLimits": (fdl, fdl)}, buffer_count=10)
    
    picam2.configure(video_config)

    picam2.start_preview(Preview.QTGL)

    encoder = JpegEncoder(q=70)
    picam2.start_recording(encoder, vid_name, pts=ts_name)
    time.sleep(duration)
    picam2.stop_recording()
    picam2.stop_preview()


rat_num = 999

# if set_trig=True (use external trigger for each frame), fps is irrelevant.
# If set_trig=False, fps determines target frame rate. With the quadrascopic OV9281,
# fps > 25 leads to dropped frames (25 seems to be OK...)
set_ext_trig_cmd = 'v4l2-ctl -d /dev/v4l-subdev0 -c trigger_mode=1'
stop_ext_trig_cmd = 'v4l2-ctl -d /dev/v4l-subdev0 -c trigger_mode=0'
set_trig=True

calibration_fps = 25
task_fps = 30    # doesn't do anything if external trigger is on
calibration_duration = 60
calibration_delay = 1
task_duration = 60    # recording Pavlovian task for 6 minutes, this can be adjusted...

task = 'pavlovian'
# parent_folder = '/home/levlab/data'
parent_folder = '/media/levlab/T7'

task_vid_name = create_vid_name(rat_num, task=task, parent_folder=parent_folder, vid_type='.mjpeg')
task_ts_name = create_ts_name(rat_num, task=task, parent_folder=parent_folder)

calibration_vid_name = create_vid_name(rat_num, task='calibration', parent_folder=parent_folder, vid_type='.mjpeg')
calibration_ts_name = create_ts_name(rat_num, task='calibration', parent_folder=parent_folder)

input("press <Enter> when ready to record calibration video")

print('seconds until recording starts:')
for i in reversed(range(0, calibration_delay)):
    time.sleep(1)
    print("%s\r " %i,end='')

picam2 = Picamera2()
record_calibration_video(picam2, calibration_vid_name, calibration_ts_name, duration=calibration_duration, fps=calibration_fps)
    
fname = create_vid_name(rat_num)

if set_trig:
    # enter external trigger mode
    os.system(set_ext_trig_cmd)
#     video_config = picam2.create_video_configuration(main={"size": (5120, 800)}, lores={"size": (320, 64)}, display="lores", buffer_count=10)
    video_config = picam2.create_video_configuration(main={"size": (5120, 800)}, buffer_count=10)
#     ts_name = 'mjpeg_ts_triggered_{:03d}fps_{:03d}sec.txt'.format(fps, vid_duration)
#     vid_name = 'mjpeg_triggered_{:03d}fps_{:03d}sec.mjpeg'.format(fps, vid_duration)
#   above left over from debugging
else:
    os.system(stop_ext_trig_cmd)
    fdl = int(1000000 / task_fps)
    video_config = picam2.create_video_configuration(main={"size": (5120, 800)}, lores={"size": (320, 64)}, display="lores", controls={"FrameDurationLimits": (fdl, fdl)}, buffer_count=10)
#     ts_name = 'mjpeg_ts_freerun_{:03d}fps_{:03d}sec.txt'.format(fps, vid_duration)
#     vid_name = 'mjpeg_freerun_{:03d}fps_{:03d}sec.mjpeg'.format(fps, vid_duration)
#   above left over from debugging

# left over from debugging
# ts_name = os.path.join(save_dir, ts_name)
# vid_name = os.path.join(save_dir, vid_name)
    
picam2.configure(video_config)

# picam2.start_preview(Preview.QTGL)

input('press <Enter> when ready to record task video')

encoder = JpegEncoder(q=70)
picam2.start_recording(encoder, task_vid_name, pts=task_ts_name)
# display countdown timer

# print('time left in recording:')
# for i in reversed(range(0, task_duration)):
#     time.sleep(1)
#     print("%s\r" %i, end='')
time.sleep(task_duration)
                 
picam2.stop_recording()
# picam2.stop_preview()

# exit external trigger mode and go back to regular frame acquisition
os.system(stop_ext_trig_cmd)

# copy data to sharedx