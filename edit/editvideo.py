import cv2
import numpy as np
import moviepy.editor as mp
import moviepy.video.fx.all as vfx
from moviepy.editor import VideoFileClip, ColorClip, clips_array,concatenate_videoclips
from moviepy.video.fx.all import resize, speedx
from moviepy.audio.fx.all import volumex, audio_fadein, audio_fadeout

class EditVideo:

    def __init__(self,input_path,setting):
        self.input_path = input_path
        self.setting = setting

    def convert_video_aspect_ratio(self, aspect_ratio="9:16"):
    # Đọc video
        clip = VideoFileClip(self.input_path)
        orig_width, orig_height = clip.size

        original_ratio = round(orig_width / orig_height, 2)
    
    # Chuyển aspect_ratio thành số thực để so sánh
        new_aspect_w, new_aspect_h = map(int, aspect_ratio.split(":"))
        target_ratio = round(new_aspect_w / new_aspect_h, 2)

        # Nếu video đã có đúng tỷ lệ mong muốn, bỏ qua việc chuyển đổi
        if original_ratio == target_ratio:
            print(f"Video đã có tỷ lệ {aspect_ratio}, không cần chuyển đổi.")
            return

        # Xác định tỷ lệ khung hình mới
        new_aspect_w, new_aspect_h = map(int, aspect_ratio.split(":"))
        new_width = 1080  # Chiều rộng chuẩn (có thể điều chỉnh)
        new_height = int(new_width * new_aspect_h / new_aspect_w)

        # Tính tỷ lệ thu nhỏ để giữ nguyên tỷ lệ video gốc
        scale_w = new_width / orig_width
        scale_h = new_height / orig_height
        scale_factor = min(scale_w, scale_h)

        # Kích thước video sau khi thu nhỏ
        resized_width = int(orig_width * scale_factor)
        resized_height = int(orig_height * scale_factor)

        def process_frame(frame):
            # Chuyển frame thành OpenCV (BGR)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Resize video theo tỷ lệ giữ nguyên
            resized_frame = cv2.resize(frame, (resized_width, resized_height))

            # Tạo khung nền đen
            background = np.zeros((new_height, new_width, 3), dtype=np.uint8)

            # Tính vị trí chèn video vào giữa
            x_offset = (new_width - resized_width) // 2
            y_offset = (new_height - resized_height) // 2

            # Chèn video vào giữa khung nền
            background[y_offset:y_offset+resized_height, x_offset:x_offset+resized_width] = resized_frame

            # Chuyển lại thành định dạng RGB cho MoviePy
            return cv2.cvtColor(background, cv2.COLOR_BGR2RGB)

        # Áp dụng xử lý từng frame
        new_clip = clip.fl_image(process_frame)

        # Xuất video
        new_clip.write_videofile(self.setting["edit_video"]["save_folder_edit_video"], codec="libx264", fps=clip.fps)

    def speed_up_video(self, factor=2):
        clip = mp.VideoFileClip(self.input_path)
        new_clip = speedx(clip, factor)
        new_clip.write_videofile(self.output_path, codec="libx264")

    def trim_video(self, mode="start"):
        clip = mp.VideoFileClip(self.input_path)
        if mode == "start":
            new_clip = clip.subclip(3, clip.duration)
        elif mode == "end":
            new_clip = clip.subclip(0, clip.duration - 3)
        elif mode == "interval":
            new_clip = mp.concatenate_videoclips([clip.subclip(i, i+1) for i in range(0, int(clip.duration), 5)])
        new_clip.write_videofile(self.output_path, codec="libx264")

    def merge_videos(self, extra_video, position="start"):
        main_clip = mp.VideoFileClip(self.input_path)
        extra_clip = mp.VideoFileClip(extra_video)
        if position == "start":
            final_clip = mp.concatenate_videoclips([extra_clip, main_clip])
        else:
            final_clip = mp.concatenate_videoclips([main_clip, extra_clip])
        final_clip.write_videofile(self.output_path, codec="libx264")

    def adjust_color(self, mode="basic", opacity=1.0, red=1.0, green=1.0, blue=1.0, 
                    brightness=1.0, saturation=1.0, gamma=1.0, hue=0.0):
        video = mp.VideoFileClip(self.input_path).fx(vfx.colorx, brightness)

        if mode == "basic":
            # Điều chỉnh màu cơ bản
            video = video.fl_image(lambda frame: np.clip(frame * [red, green, blue], 0, 255).astype(np.uint8))
            video = video.set_opacity(opacity)
        
        elif mode == "advanced":
            # Điều chỉnh saturation, gamma, hue
            video = video.fx(vfx.colorx, saturation)
            video = video.fx(vfx.gamma_corr, gamma)
            video = video.fx(vfx.hue, hue)

        video.write_videofile(self.output_path, codec="libx264", fps=video.fps)

    def adjust_volume(self, volume_factor=1.0):
        clip = mp.VideoFileClip(self.input_path)
        new_clip = clip.volumex(volume_factor)
        new_clip.write_videofile(self.output_path, codec="libx264", audio_codec="aac")

    def add_background_music(self, music_path, volume=0.5):
        video_clip = mp.VideoFileClip(self.input_path)
        audio_clip = mp.AudioFileClip(music_path).volumex(volume).set_duration(video_clip.duration)
        final_audio = mp.CompositeAudioClip([video_clip.audio, audio_clip])
        video_clip = video_clip.set_audio(final_audio)
        video_clip.write_videofile(self.output_path, codec="libx264", audio_codec="aac")

    def distort_audio(self,audio_fadein, audio_fadeout,fade_type="in", duration=3):
        video_clip = mp.VideoFileClip(self.input_path)
        if fade_type == "in":
            audio_clip = video_clip.audio.fx(audio_fadein, duration)
        else:
            audio_clip = video_clip.audio.fx(audio_fadeout, duration)
        video_clip = video_clip.set_audio(audio_clip)
        video_clip.write_videofile(self.output_path, codec="libx264", audio_codec="aac")

    def merge_videos(video1_path, video2_path, output_path):
        clip1 = VideoFileClip(video1_path)
        clip2 = VideoFileClip(video2_path)

        # Xác định thời lượng lớn nhất
        max_duration = max(clip1.duration, clip2.duration)

        def pad_video(clip, target_duration):
            if clip.duration < target_duration:
                black_bg = ColorClip(size=(clip.w, clip.h), color=(0, 0, 0), duration=target_duration - clip.duration)
                return concatenate_videoclips([clip, black_bg])
            return clip

        clip1 = pad_video(clip1, max_duration)
        clip2 = pad_video(clip2, max_duration)

        # Điều chỉnh kích thước video để có cùng chiều rộng hoặc chiều cao
        if mode == "horizontal":
            new_height = min(clip1.h, clip2.h)  # Đảm bảo cùng chiều cao
            clip1 = clip1.resize(height=new_height)
            clip2 = clip2.resize(height=new_height)
            final_clip = clips_array([[clip1, clip2]])  # Ghép ngang
        else:
            new_width = min(clip1.w, clip2.w)  # Đảm bảo cùng chiều rộng
            clip1 = clip1.resize(width=new_width)
            clip2 = clip2.resize(width=new_width)
            final_clip = clips_array([[clip1], [clip2]])  # Ghép dọc

        # Xuất video cuối cùng
        final_clip.write_videofile(output_path, codec="libx264", fps=clip1.fps)
 
    def run(self):
        frame = ""
        if self.setting["edit_video"]["frame"] == "1":
            frame = "16:9"
        elif self.setting["edit_video"]["frame"] == "2":
            frame = "9:16"
        elif self.setting["edit_video"]["frame"] == "3":
            frame = "4:3"

        speed = 1
        if self.setting["edit_video"]["speed_video"] == "2":
            speed = 2
        elif self.setting["edit_video"]["speed_video"] == "3":
            speed = 4

        if self.setting["edit_video"]["speed_video_custom"] != "0":
            speed = int(self.setting["edit_video"]["speed_video_custom"])

        cut = "start"
        if self.setting["edit_video"]["cut_video"] == "1":
            frame = "start"
        elif self.setting["edit_video"]["cut_video"] == "2":
            frame = "end"
        elif self.setting["edit_video"]["cut_video"] == "3":
            frame = "interval"

        intro = self.setting["edit_video"]["intro_video"]
        outtro = self.setting["edit_video"]["outro_video"]

        left_video = self.setting["edit_video"]["left_video"]
        right_video = self.setting["edit_video"]["right_video"]

        top_video = self.setting["edit_video"]["top_video"]
        bottom_video = self.setting["edit_video"]["bottom_video"]

        if

        

        



            
        
