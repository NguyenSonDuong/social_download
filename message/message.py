from enum import Enum
class Message:
    def __init__(self):
        pass
    class NotificationType(Enum):
        NOTIFICATION = 0
        ERROR = 1
        WARNING = 2
    class Youtube:
        message_get_info_channel_start = "Bắt đầu lấy thông tin kênh"
        message_get_info_channel_success = "Lấy thông tin kênh thành công"
        message_get_info_channel_error = "Lấy thông tin kênh THẤT BẠI!!"
        message_get_info_channel_process = "Đảng tải video: "
    class Douyin:
        message_get_info_channel_start_browser = "Bắt đầu lấy thông tin trang"
        message_get_info_channel_start_download = "Bắt đầu tải video"
        message_get_info_channel_success_browser = "Đã lấy thông tin kênh xong"
        message_get_info_channel_success_download = "Tải video thành công"
        message_get_info_channel_error = "Lấy thông tin kênh THẤT BẠI!!"
        message_get_info_channel_error_download = "Tải video THÁT BẠI!!"
        message_get_info_channel_error_url = "Lấy thông tin url THẤT BẠI!!"
        message_get_info_channel_process_url = "Đang lấy đường dẫn url..."
        message_get_info_channel_process = "Đảng tải video: "