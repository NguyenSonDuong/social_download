import cv2
import numpy as np
import moviepy.editor as mp
import moviepy.video.fx.all as vfx
from moviepy.video.fx.all import resize, speedx
from moviepy.audio.fx.all import volumex, audio_fadein, audio_fadeout

def change_aspect_ratio(input_path, output_path, aspect_ratio="16:9"):
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    aspect_ratios = {"16:9": (1920, 1080), "9:16": (1080, 1920), "4:3": (1440, 1080)}
    new_width, new_height = aspect_ratios.get(aspect_ratio, (width, height))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (new_width, new_height))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (new_width, new_height))
        out.write(frame)
    
    cap.release()
    out.release()

def speed_up_video(input_path, output_path, factor=2):
    clip = mp.VideoFileClip(input_path)
    new_clip = speedx(clip, factor)
    new_clip.write_videofile(output_path, codec="libx264")



def trim_video(input_path, output_path, mode="start"):
    clip = mp.VideoFileClip(input_path)
    if mode == "start":
        new_clip = clip.subclip(3, clip.duration)
    elif mode == "end":
        new_clip = clip.subclip(0, clip.duration - 3)
    elif mode == "interval":
        new_clip = mp.concatenate_videoclips([clip.subclip(i, i+1) for i in range(0, int(clip.duration), 5)])
    new_clip.write_videofile(output_path, codec="libx264")

def merge_videos(main_video, extra_video, output_path, position="start"):
    main_clip = mp.VideoFileClip(main_video)
    extra_clip = mp.VideoFileClip(extra_video)
    if position == "start":
        final_clip = mp.concatenate_videoclips([extra_clip, main_clip])
    else:
        final_clip = mp.concatenate_videoclips([main_clip, extra_clip])
    final_clip.write_videofile(output_path, codec="libx264")

def adjust_color(input_path, output_path, mode="basic", opacity=1.0, red=1.0, green=1.0, blue=1.0, 
                 brightness=1.0, saturation=1.0, gamma=1.0, hue=0.0):
    video = mp.VideoFileClip(input_path).fx(vfx.colorx, brightness)

    if mode == "basic":
        # Điều chỉnh màu cơ bản
        video = video.fl_image(lambda frame: np.clip(frame * [red, green, blue], 0, 255).astype(np.uint8))
        video = video.set_opacity(opacity)
    
    elif mode == "advanced":
        # Điều chỉnh saturation, gamma, hue
        video = video.fx(vfx.colorx, saturation)
        video = video.fx(vfx.gamma_corr, gamma)
        video = video.fx(vfx.hue, hue)

    video.write_videofile(output_path, codec="libx264", fps=video.fps)


def adjust_volume(input_path, output_path, volume_factor=1.0):
    clip = mp.VideoFileClip(input_path)
    new_clip = clip.volumex(volume_factor)
    new_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

def add_background_music(input_path, music_path, output_path, volume=0.5):
    video_clip = mp.VideoFileClip(input_path)
    audio_clip = mp.AudioFileClip(music_path).volumex(volume).set_duration(video_clip.duration)
    final_audio = mp.CompositeAudioClip([video_clip.audio, audio_clip])
    video_clip = video_clip.set_audio(final_audio)
    video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

def distort_audio(input_path, output_path, fade_type="in", duration=3):
    video_clip = mp.VideoFileClip(input_path)
    if fade_type == "in":
        audio_clip = video_clip.audio.fx(audio_fadein, duration)
    else:
        audio_clip = video_clip.audio.fx(audio_fadeout, duration)
    video_clip = video_clip.set_audio(audio_clip)
    video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

