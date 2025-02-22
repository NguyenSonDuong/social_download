import subprocess
import re
import os
import unicodedata
import ffmpeg
import cv2
import numpy as np
from moviepy import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
import  moviepy.video.fx as vfx
from moviepy.video.VideoClip import ColorClip
from moviepy.video.compositing.CompositeVideoClip import clips_array
class EditStatus:
    START = 0
    PROCESS = 1
    DONE = 2
    ERROR = -1
    DONE_ONE = 3
class EditVideo:

    _processDownload = None
    _processError = None

    def __init__(self,processDownload,processError,setting, isEdit = False, isColor = False, isAudio = False):
        self.setting = setting
        self._processDownload = processDownload
        self._processError = processError
        self.isEdit = isEdit
        self.isColor = isColor
        self.isAudio = isAudio

    def remove_accents(self,input_str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        only_ascii = nfkd_form.encode('ASCII', 'ignore')
        return only_ascii.decode('utf-8')


    def upSpeed(self,clip, speed):
        sped_up_clip = vfx.MultiplySpeed(speed).apply(clip)
        return sped_up_clip
    def cutEndStart(self, clip, start, end):
        if start:
            clip = clip.subclipped(start, clip.duration)
        if end:
            clip = clip.subclipped(0, clip.duration - end)
        
        return clip

    def ColorBalance(self,clip, opacity, red, green, blue,brightness, saturation, gamma, hue, contrast):
        if opacity:
            clip = clip.image_transform(lambda image: image * opacity)
        if red:
            clip = clip.image_transform(lambda image: image * red)
        if green:
            clip = clip.image_transform(lambda image: image * green)
        if blue:
            clip = clip.image_transform(lambda image: image * blue)
        if brightness:
            clip = clip.image_transform(lambda image: image * brightness)
        if saturation:
            clip = clip.image_transform(lambda image: image * saturation)
        if gamma:
            clip = clip.image_transform(lambda image: image * gamma)
        if hue:
            clip = clip.image_transform(lambda image: image * hue)
        if contrast:
            clip = clip.image_transform(lambda image: image * contrast)
        return clip

    def add_black_borders(self,clip, target_aspect_ratio):

    # Xác định tỷ lệ khung hình mới
        orig_width, orig_height = clip.size
        new_aspect_w, new_aspect_h = map(int, target_aspect_ratio.split(":"))
        
        if orig_width / orig_height > new_aspect_w / new_aspect_h:
            new_width = orig_width
            new_height = int(new_width * new_aspect_h / new_aspect_w)
        else:
            new_height = orig_height
            new_width = orig_height * new_aspect_w // new_aspect_h 
        
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
        new_clip = clip.image_transform(process_frame)

        return new_clip
    
    def add_intro_outro(self, stream, intro_file, outro_file,target_aspect_ratio):

        main_app = []
        if intro_file:
            intro_clip = VideoFileClip(intro_file)
            intro_clip = self.add_black_borders(intro_clip, target_aspect_ratio)
            main_app.append(intro_clip)
        main_app.append(stream)
        if outro_file:
            outro_clip = VideoFileClip(outro_file)
            outro_clip = self.add_black_borders(outro_clip, target_aspect_ratio)
            main_app.append(outro_clip)
        final_clip = concatenate_videoclips(main_app)
        return final_clip

    def cut_every_5s(self,clip):
        duration = clip.duration
        clips = []
        
        for start in range(0, int(duration), 5):
            end = min(start + 4, duration)
            if start < end:
                subclip = clip.subclipped(start, end)
                clips.append(subclip)
        
        final_clip = concatenate_videoclips(clips)
        return final_clip

    def edit_video2(self,
            input_path, output_path,
            aspect_ratio=None, speed=None,
            cut_start=None, cut_end=None, cut_interval=None,
            bg_path=None, intro_path=None, outro_path=None,
            opacity=None, red=None, green=None, blue=None,
            brightness=None, saturation=None, gamma=None, hue=None, contrast=None,
            bg_music=None, flip_horizontal=False, flip_vertical=False
        ):
        # 📌 Danh sách filters
        filters = []
        if self.isEdit:
            # 📌 Thay đổi khung hình
            if aspect_ratio == "16:9":
                filters.append("scale=w=min(iw\\,1920):h=-2, pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black")
            elif aspect_ratio == "9:16":
                filters.append("scale=h=min(ih\\,1920):w=-2, pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black")
            elif aspect_ratio == "4:3":
                filters.append("scale=w=min(iw\\,1440):h=-2, pad=1440:1080:(ow-iw)/2:(oh-ih)/2:black")

            # 📌 Tăng tốc độ video
            if speed is not None:
                filters.append(f"setpts={1/speed}*PTS")

            # 📌 Lật video
            if flip_horizontal:
                filters.append("hflip")
            if flip_vertical:
                filters.append("vflip")

            # 📌 Cắt video
            if cut_start:
                filters.append(f"trim=start={cut_start}")
            if cut_end:
                filters.append(f"trim=end={cut_end}")
            if cut_interval:
                filters.append("select='not(mod(n,150))',setpts=N/FRAME_RATE/TB")

        if self.isColor:
            # 📌 Chỉnh sửa màu sắc
            color_filter = []
            if opacity is not None:
                color_filter.append(f"colorchannelmixer=aa={opacity}")
            if red is not None:
                color_filter.append(f"colorchannelmixer=rr={red}")
            if green is not None:
                color_filter.append(f"colorchannelmixer=gg={green}")
            if blue is not None:
                color_filter.append(f"colorchannelmixer=bb={blue}")
            if brightness is not None:
                color_filter.append(f"eq=brightness={brightness}")
            if saturation is not None:
                color_filter.append(f"eq=saturation={saturation}")
            if gamma is not None:
                color_filter.append(f"eq=gamma={gamma}")
            if hue is not None:
                color_filter.append(f"hue=h={hue}")
            if contrast is not None:
                color_filter.append(f"eq=contrast={contrast}")

            if color_filter:
                filters.append(",".join(color_filter))




        # 📌 Thêm background video hoặc ảnh
        # if bg_path:
        #     filters.append(f"[1:v]scale=1280:720[bg];[bg][0:v]overlay=W/2-w/2:H/2-h/2")

        # 📌 Tạo chuỗi filter
        filter_str = ",".join(filters) if filters else "null"

        # 📌 Lệnh FFmpeg
        # cmd = ["ffmpeg", "-i", input_path, "-vf", filter_str]

        # 📌 Thêm background video hoặc ảnh
        # if bg_path:
        #     cmd = ["ffmpeg", "-i", bg_path, "-i", input_path, "-filter_complex", filter_str]

        # 📌 Thêm nhạc nền
        # if bg_music:
        #     cmd += ["-i", bg_music, "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=3"]
        # if self.isEdit:
        #     # 📌 Lồng intro/outro
        #     if intro_path or outro_path:
        #         temp_video = "temp_video.mp4"
        #         subprocess.run(cmd + ["-c:v", "libx264", "-preset", "fast", temp_video])
        #         concat_cmd = [
        #             "ffmpeg", "-i", intro_path, "-i", temp_video, "-i", outro_path,
        #             "-filter_complex", "[0:v:0][0:a:0][1:v:0][1:a:0][2:v:0][2:a:0]concat=n=3:v=1:a=1[outv][outa]",
        #             "-map", "[outv]", "-map", "[outa]", output_path
        #         ]
        #         subprocess.run(concat_cmd)
        #         return
        #
        # # 📌 Ghép video (trái/phải/trên/dưới)
        # # if merge_with:
        # #     merge_filter = "[0:v][1:v]hstack=inputs=2[v]" if merge_type == "side" else "[0:v][1:v]vstack=inputs=2[v]"
        # #     cmd = ["ffmpeg", "-i", input_path, "-i", merge_with, "-filter_complex", merge_filter, "-map", "[v]", output_path]
        # # else:
        # cmd += [ self.remove_accents(output_path)]
        # # cmd += ["-map 0:a -c:a libmp3lame" , f"{ output_path.substring(0, output_path.lastIndexOf('.'))}.mp4"]
        #
        # # 📌 Chạy lệnh FFmpeg
        # subprocess.run(cmd)
        # process = subprocess.Popen(
        #     cmd,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     universal_newlines=True,
        #     bufsize=1
        # )
        # for line in process.stderr:
        #     # Lấy tổng thời lượng video
        #     if duration is None:
        #         match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", line)
        #         if match:
        #             h, m, s = map(float, match.groups())
        #             duration = h * 3600 + m * 60 + s  # Chuyển thành giây

        #     # Lấy thời gian hiện tại của video (progress)
        #     match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
        #     if match:
        #         h, m, s = map(float, match.groups())
        #         current_time = h * 3600 + m * 60 + s  # Chuyển thành giây

        #         if duration:
        #             progress = (current_time / duration) * 100
        #             print(f"Tiến trình: {progress:.2f}%")
        # process.wait()

    def edit_video(self, 
                  input_path, 
                  output_path, 
                  aspect_ratio=None, 
                  speed=None, 
                  cut_start=None, 
                  cut_end=None, 
                  cut_interval=None, 
                  bg_path=None, 
                  intro_path=None, 
                  outro_path=None, 
                  opacity=None, 
                  red=None, green=None, blue=None, brightness=None, 
                  saturation=None, gamma=None, hue=None, contrast=None, 
                  bg_music=None, flip_horizontal=False, flip_vertical=False):
        stream = ffmpeg.input(input_path)
        if self.isEdit:
            
            if speed:
                stream = stream.setpts(f'PTS/{speed}')
            
            # Cắt video
            if cut_end or cut_start:
                if cut_start:
                    stream = stream.trim(start=cut_start)
                if cut_end:
                    stream = stream.trim(end=cut_end)
            if cut_interval:
                stream = stream.filter('select', 'not(mod(t,5))')
                stream = stream.setpts('N/FRAME_RATE/TB')


            if intro_path and outro_path:
                intro = ffmpeg.input(intro_path)
                outro = ffmpeg.input(outro_path)
                stream = ffmpeg.concat(intro, ffmpeg.concat(intro, stream, outro))

        # if overlay_file and overlay_position:
        #     overlay = ffmpeg.input(overlay_file)
        #     if overlay_position == 'top':
        #         stream = ffmpeg.overlay(stream, overlay, x=0, y=0)
        #     elif overlay_position == 'bottom':
        #         stream = ffmpeg.overlay(stream, overlay, x=0, y='main_h-overlay_h')
        #     elif overlay_position == 'left':
        #         stream = ffmpeg.overlay(stream, overlay, x=0, y=0)
        #     elif overlay_position == 'right':
        #         stream = ffmpeg.overlay(stream, overlay, x='main_w-overlay_w', y=0)
        if self.isColor:
            if opacity:
                stream = stream.filter('colorchannelmixer', a=opacity)
            stream = stream.filter('colorbalance', rgain=red if red is not None else 1.0, ggain=green if green is not None else 1.0, bgain=blue if blue is not None else 1.0)
            if brightness is not None:
                stream = stream.filter('eq', brightness=brightness)
            if saturation is not None:
                stream = stream.filter('eq', saturation=saturation)
            if gamma is not None:
                stream = stream.filter('eq', gamma=gamma)
            if hue is not None:
                stream = stream.filter('hue', h=hue)
                
        if aspect_ratio:
            stream.output(self.convert_to_mp4(self.remove_accents(output_path))).run()
        else:
            stream.output(self.convert_to_mp4(self.remove_accents(output_path))).run()

    def merge_videos(main_video, extra_video, output_path, position="right"):
        # 📌 Lấy thời lượng video
        get_duration_cmd = lambda vid: f'ffprobe -i "{vid}" -show_entries format=duration -v quiet -of csv="p=0"'
        main_duration = float(subprocess.check_output(get_duration_cmd(main_video), shell=True).decode().strip())
        extra_duration = float(subprocess.check_output(get_duration_cmd(extra_video), shell=True).decode().strip())

        max_duration = max(main_duration, extra_duration)

        # 📌 Tạo video nền đen nếu video ngắn hơn
        black_bg = f"color=c=black:s=1920x1080:d={max_duration}[black];"
        
        if main_duration < max_duration:
            main_pad = f"[0:v]trim=duration={main_duration},setpts=PTS-STARTPTS,pad=1920:1080:black[main_vid];"
        else:
            main_pad = "[0:v]setpts=PTS-STARTPTS[main_vid];"

        if extra_duration < max_duration:
            extra_pad = f"[1:v]trim=duration={extra_duration},setpts=PTS-STARTPTS,pad=1920:1080:black[extra_vid];"
        else:
            extra_pad = "[1:v]setpts=PTS-STARTPTS[extra_vid];"

        # 📌 Xác định cách ghép video
        if position == "left":
            merge_filter = "[main_vid]scale=960:1080[right];[extra_vid]scale=960:1080[left];[left][right]hstack=inputs=2[outv]"
        elif position == "right":
            merge_filter = "[main_vid]scale=960:1080[left];[extra_vid]scale=960:1080[right];[left][right]hstack=inputs=2[outv]"
        elif position == "top":
            merge_filter = "[main_vid]scale=1920:540[bottom];[extra_vid]scale=1920:540[top];[top][bottom]vstack=inputs=2[outv]"
        elif position == "bottom":
            merge_filter = "[main_vid]scale=1920:540[top];[extra_vid]scale=1920:540[bottom];[top][bottom]vstack=inputs=2[outv]"
        else:
            raise ValueError("Vị trí không hợp lệ! Chọn: left, right, top, bottom.")

        # 📌 Chạy FFmpeg
        ffmpeg_cmd = f'ffmpeg -i "{main_video}" -i "{extra_video}" -filter_complex "{black_bg}{main_pad}{extra_pad}{merge_filter}" -map "[outv]" -map 0:a? -map 1:a? -shortest "{output_path}"'
        
        subprocess.run(ffmpeg_cmd, shell=True)

    def convert_to_mp4(self,file_path):
        # Lấy tên file mà không bao gồm đuôi file
        name_without_ext, _ = os.path.splitext(os.path.basename(file_path))
        # Tạo tên file đầu ra với đuôi .mp4
        output_file = os.path.join(os.path.dirname(file_path), f"{name_without_ext}.mp4")
        return output_file
    
    def run(self, input_video):
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
            cut = "start"
        elif self.setting["edit_video"]["cut_video"] == "2":
            cut = "end"
        elif self.setting["edit_video"]["cut_video"] == "3":
            cut = "interval"


        intro = self.setting["edit_video"]["intro_video"]
        outtro = self.setting["edit_video"]["outro_video"]

        left_video = self.setting["edit_video"]["left_video"]
        right_video = self.setting["edit_video"]["right_video"]

        top_video = self.setting["edit_video"]["top_video"]
        bottom_video = self.setting["edit_video"]["bottom_video"]
        ten_file = os.path.basename(input_video)
        folder_save =  f"{self.setting["edit_video"]["save_folder_edit_video"]}/{ten_file}"

        opacity = None if self.setting["color"]["opacity"] is None else float(self.setting["color"]["opacity"])
        red = None if self.setting["color"]["red"] is None else float(self.setting["color"]["red"])
        green = None if self.setting["color"]["green"] is None else float(self.setting["color"]["green"])
        blue = None if self.setting["color"]["blue"] is None else float(self.setting["color"]["blue"])
        brightness =  None if self.setting["color"]["birghtness"] is None else float(self.setting["color"]["birghtness"])
        saturation = None if self.setting["color"]["saturation"] is None else float(self.setting["color"]["saturation"])
        gamma = None if self.setting["color"]["gamma"] is None else float(self.setting["color"]["gamma"])
        hue = None if self.setting["color"]["hue"] is None else float(self.setting["color"]["hue"])
        contrast = None

        if self.isEdit:
            stream = VideoFileClip(input_video)
            if speed:
                stream = self.upSpeed(stream, speed)

            stream = self.cutEndStart(stream, 3 if cut == "start" else None, 3 if cut == "end" else None)
            if cut == "interval" :
                stream = self.cut_every_5s(stream)
            
            if frame:
                stream = self.add_black_borders(stream, frame)
            if intro or outtro:
                stream = self.add_intro_outro(stream, intro, outtro,frame)

            stream = self.ColorBalance(stream, opacity, red, green, blue,brightness, saturation, gamma, hue, contrast)

            if left_video or right_video:
                self.merge_videos(stream, right_video, "right")
            if top_video or bottom_video:
                self.merge_videos(stream, bottom_video, "bottom")

            stream.write_videofile(self.convert_to_mp4(self.remove_accents(folder_save)), codec='libx264')

        # self.edit_video(
        #     input_path=input_video,
        #     output_path=folder_save,
        #     aspect_ratio=frame,
        #     speed=speed,
        #     cut_start= 3 if cut == "start" else None ,
        #     cut_end=3 if cut == "end" else None,
        #     cut_interval= True if cut == "interval" else None,
        #     bg_path= None,
        #     intro_path=intro,
        #     outro_path=outtro,
        #     opacity=opacity, red=red, green=green, blue=blue,
        #     brightness=brightness, saturation=saturation, gamma=gamma, hue=hue, contrast=contrast,
        #     bg_music=None,
        #     flip_horizontal=None,
        #     flip_vertical=None
        # )

    def merge_videos(self,clip1, video2_path, mode="va"):
    # Đọc hai video
    # Đọc hai video
        clip2 = VideoFileClip(video2_path)

        # Xác định thời lượng lớn nhất
        max_duration = max(clip1.duration, clip2.duration)

        # Đảm bảo cả hai video có cùng thời lượng bằng cách thêm nền đen vào video ngắn hơn
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

        return final_clip



        



            
        
