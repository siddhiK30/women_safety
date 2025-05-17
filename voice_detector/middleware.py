from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .utils import VoiceDetector
from .models import UserAlertConfig


# Global dictionary to store user voice detectors
voice_detectors = {}

@receiver(user_logged_in)
def start_voice_detection(sender, user, request, **kwargs):
    """Start voice detection when user logs in"""
    if user.id not in voice_detectors:
        config = UserAlertConfig.objects.get_or_create(user=user)[0]
        detector = VoiceDetector()
        detector.start_detection(config)
        voice_detectors[user.id] = detector

@receiver(user_logged_out)
def stop_voice_detection(sender, user, request, **kwargs):
    """Stop voice detection when user logs out"""
    if user.id in voice_detectors:
        voice_detectors[user.id].stop_detection()
        del voice_detectors[user.id]
