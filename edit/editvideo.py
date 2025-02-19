import subprocess
import os

class EditVideo:

    def __init__(self,input_path,setting):
        self.input_path = input_path
        self.setting = setting


    def edit_video(
            input_path, output_path,
            aspect_ratio=None, speed=None,
            cut_start=None, cut_end=None, cut_interval=None,
            bg_path=None, intro_path=None, outro_path=None,
            merge_with=None, merge_type="side",
            opacity=None, red=None, green=None, blue=None,
            brightness=None, saturation=None, gamma=None, hue=None, contrast=None,
            bg_music=None, flip_horizontal=False, flip_vertical=False
        ):
        filters = []

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

        # 📌 Thêm background video hoặc ảnh
        if bg_path:
            filters.append(f"[1:v]scale=1280:720[bg];[bg][0:v]overlay=W/2-w/2:H/2-h/2")

        # 📌 Tạo chuỗi filter
        filter_str = ",".join(filters) if filters else "null"

        # 📌 Lệnh FFmpeg
        cmd = ["ffmpeg", "-i", input_path, "-vf", filter_str]

        # 📌 Thêm background video hoặc ảnh
        if bg_path:
            cmd = ["ffmpeg", "-i", bg_path, "-i", input_path, "-filter_complex", filter_str]

        # 📌 Thêm nhạc nền
        if bg_music:
            cmd += ["-i", bg_music, "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=3"]

        # 📌 Lồng intro/outro
        if intro_path or outro_path:
            temp_video = "temp_video.mp4"
            subprocess.run(cmd + ["-c:v", "libx264", "-preset", "fast", temp_video])
            concat_cmd = [
                "ffmpeg", "-i", intro_path, "-i", temp_video, "-i", outro_path,
                "-filter_complex", "[0:v:0][0:a:0][1:v:0][1:a:0][2:v:0][2:a:0]concat=n=3:v=1:a=1[outv][outa]",
                "-map", "[outv]", "-map", "[outa]", output_path
            ]
            subprocess.run(concat_cmd)
            return
        
        # 📌 Ghép video (trái/phải/trên/dưới)
        if merge_with:
            merge_filter = "[0:v][1:v]hstack=inputs=2[v]" if merge_type == "side" else "[0:v][1:v]vstack=inputs=2[v]"
            cmd = ["ffmpeg", "-i", input_path, "-i", merge_with, "-filter_complex", merge_filter, "-map", "[v]", output_path]
        else:
            cmd += ["-c:v", "libx264", "-preset", "fast", output_path]

        # 📌 Chạy lệnh FFmpeg
        subprocess.run(cmd)

    def merge_videos(
        main_video, extra_video, output_path, position="right"
    ):
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

        # edit_video(
        #     input_path="input.mp4",
        #     output_path="output.mp4",
        #     aspect_ratio=frame,
        #     speed=speed,
        #     cut_start=3, 
        #     cut_end=3, 
        #     cut_interval=True,
        #     bg_path="background.jpg",
        #     intro_path=intro, 
        #     outro_path=outtro,
        #     merge_with="video2.mp4", 
        #     merge_type="side",
        #     opacity=0.5, red=1.2, green=1.1, blue=0.9,
        #     brightness=0.1, saturation=1.2, gamma=1.5, hue=0.05, contrast=1.3,
        #     bg_music="music.mp3",
        #     flip_horizontal=True, 
        #     flip_vertical=False
        # )
 


        

        



            
        
