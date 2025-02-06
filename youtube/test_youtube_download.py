import unittest
import yt_dlp
import sys
sys.path.append('.')
from youtube.youtube_download import Youtube
from youtube.youtube_key import YoutubeKey, Option
from message.message import Message

class TestYoutube(unittest.TestCase):

    def test_quick_sort_view(self):
        videos1 = [
            {'title': 'Video 1', 'view_count': 1000},
            {'title': 'Video 2', 'view_count': 500},
            {'title': 'Video 3', 'view_count': 1500},
        ]
        expected1 = [
            {'title': 'Video 2', 'view_count': 500},
            {'title': 'Video 1', 'view_count': 1000},
            {'title': 'Video 3', 'view_count': 1500},
        ]
        youtube = Youtube()
        sorted_videos1 = youtube.quick_sort_view(videos1)
        self.assertEqual(sorted_videos1, expected1)

        videos2 = [
            {'title': 'Video 1', 'view_count': 1000},
            {'title': 'Video 2', 'view_count': 1000},
            {'title': 'Video 3', 'view_count': 1500},
        ]
        expected2 = [
            {'title': 'Video 1', 'view_count': 1000},
            {'title': 'Video 2', 'view_count': 1000},
            {'title': 'Video 3', 'view_count': 1500},
        ]
        sorted_videos2 = youtube.quick_sort_view(videos2)
        self.assertEqual(sorted_videos2, expected2)

        videos3 = []
        expected3 = []
        sorted_videos3 = youtube.quick_sort_view(videos3)
        self.assertEqual(sorted_videos3, expected3)

    from unittest.mock import patch

    @patch('yt_dlp.YoutubeDL')
    def test_get_list_video(self, mock_yt_dlp):
        # Configure the mock to return a predefined channel info
        mock_ydl = mock_yt_dlp.return_value
        mock_ydl.extract_info.return_value = {
            'title': 'Test Channel',
            'entries': [
                {'entries': [{'title': 'Video 1', 'url': 'url1', 'view_count': 100}, {'title': 'Video 2', 'url': 'url2', 'view_count': 200}]},
                {'entries': [{'title': 'Short 1', 'url': 'short_url1', 'view_count': 50}, {'title': 'Short 2', 'url': 'short_url2', 'view_count': 150}]}
            ]
        }

        # Create a Youtube object with a mock process and options
        youtube = Youtube()
        youtube.option = Option()
        youtube.option.channel_url = 'https://www.youtube.com/channel/testchannel'
        youtube.option.video_type = YoutubeKey.VideoType.VIDEO
        youtube.option.video_sort = YoutubeKey.VideoSort.PHOBIEN
        youtube.option.count = 2

        # Call the get_list_video method
        videos = youtube.get_list_video()

        # Assert that the method returns the correct list of videos
        self.assertEqual(len(videos), 2)
        self.assertEqual(videos[0]['title'], 'Video 1')
        self.assertEqual(videos[1]['title'], 'Video 2')

    @patch('yt_dlp.YoutubeDL')
    def test_download_video(self, mock_yt_dlp):
        # Configure the mock to return True for successful download
        mock_ydl = mock_yt_dlp.return_value
        mock_ydl.download.return_value = True

        # Create a Youtube object with a mock process and options
        youtube = Youtube()
        youtube.option = Option()
        youtube.option.video_quatity = "bestvideo+bestaudio"
        youtube.option.output_path = "Downloads"

        # Call the download_video method
        video_url = 'https://www.youtube.com/watch?v=testvideo'
        result = youtube.download_video(video_url)

        # Assert that the method returns True
        self.assertTrue(result)

    @patch('yt_dlp.YoutubeDL')
    def test_download_videos(self, mock_yt_dlp):
        # Configure the mock to return True for successful download
        mock_ydl = mock_yt_dlp.return_value
        mock_ydl.download.return_value = True

        # Create a Youtube object with a mock process and options
        youtube = Youtube()
        youtube.option = Option()
        youtube.option.video_quatity = "bestvideo+bestaudio"
        youtube.option.output_path = "Downloads"

        # Create a list of videos to download
        videos = [
            {'title': 'Video 1', 'url': 'https://www.youtube.com/watch?v=testvideo1'},
            {'title': 'Video 2', 'url': 'https://www.youtube.com/watch?v=testvideo2'},
        ]

        # Call the download_videos method
        success_videos, error_videos = youtube.download_videos(videos)

        # Assert that the method returns the correct lists of videos
        self.assertEqual(len(success_videos), 2)
        self.assertEqual(len(error_videos), 0)
        self.assertEqual(success_videos[0]['title'], 'Video 1')
        self.assertEqual(success_videos[1]['title'], 'Video 2')

if __name__ == '__main__':
    unittest.main()
