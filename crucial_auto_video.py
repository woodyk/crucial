#!/usr/bin/env python3
#
# crucial_auto_video.py

import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont
import shutil
from pathlib import Path

def save_frame(frame_filename, directory="video_frames"):
    # Ensure the target directory exists, if not, create it
    Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Move or copy the frame to the designated directory
    target_path = Path(directory) / frame_filename
    shutil.move(frame_filename, target_path)

def generate_frame(data, frame_number):
    # Create an image with white background
    img = Image.new('RGB', (800, 600), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Use a basic font and write data onto the image
    font = ImageFont.load_default()
    d.text((10,10), data, fill=(0,0,0), font=font)
    
    # Save the frame with a unique filename based on frame number
    frame_filename = f'frame_{frame_number}.png'
    img.save(frame_filename)
    return frame_filename

# Main loop to read data piped through "|"
for line in sys.stdin:
    data = line.strip()
    cnt = 500
    while cnt <= 500:
        cnt = cnt - 1
        frame = generate_frame(data, cnt)
    # Save frame for final video
    save_frame(frame)
    # Optionally, use FFmpeg subprocess to append frame to video stream
    subprocess.call(['ffmpeg', 'arguments', 'to', 'add', 'frame', 'to', 'video'])

# Example FFmpeg command to compile saved frames into a video
subprocess.call(['ffmpeg', '-i', 'frame_%04d.png', '-output', 'final_video.mp4'])
