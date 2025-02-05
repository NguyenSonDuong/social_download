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