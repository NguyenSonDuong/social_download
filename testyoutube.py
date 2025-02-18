import cv2
import numpy as np
from moviepy.editor import VideoFileClip, ColorClip, clips_array,concatenate_videoclips

def convert_video_aspect_ratio(input_path, output_path, aspect_ratio="9:16"):
    # Đọc video
    clip = VideoFileClip(input_path)
    orig_width, orig_height = clip.size

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
    new_clip.write_videofile(output_path, codec="libx264", fps=clip.fps)

# Ví dụ sử dụng
# convert_video_aspect_ratio("E:\downloadvideo\QUY-TẦM-REMIX-BT-REMIX-归寻-等什么君-Nhạc-Trung-Remix-Hot-TikTok.webm", "output.mp4", "9:16")
def merge_videos(video1_path, video2_path, output_path, mode="va"):
    # Đọc hai video
    # Đọc hai video
    clip1 = VideoFileClip(video1_path)
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

    # Xuất video cuối cùng
    final_clip.write_videofile(output_path, codec="libx264", fps=clip1.fps)

merge_videos("E:\downloadvideo\QUY-TẦM-REMIX-BT-REMIX-归寻-等什么君-Nhạc-Trung-Remix-Hot-TikTok.webm", "E:\downloadvideo\One-More-Night-Maroon-5-Noper-Remix-Nhac-Remix-Hot-Trend-Tiktok.webm","ouy.mp4")