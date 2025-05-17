# voice_detector/apps.py
from django.apps import AppConfig

class VoiceDetectorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'voice_detector'

    def ready(self):
        from django.contrib.auth.signals import user_logged_in, user_logged_out
        from .middleware import start_voice_detection, stop_voice_detection
        
        user_logged_in.connect(start_voice_detection)
        user_logged_out.connect(stop_voice_detection)