from embed_video.backends import YoutubeBackend

class SecureYoutubeBackend(YoutubeBackend):
    is_secure = True