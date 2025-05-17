import json
import pyaudio
import time
from vosk import Model, KaldiRecognizer
from twilio.rest import Client
from django.conf import settings
import threading
from geopy.geocoders import Nominatim

class VoiceDetector:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.consecutive_help_count = 3
        self.last_detection_time = 0
        self.is_running = False
        
        # Initialize Vosk model
        self.model = Model(settings.VOSK_MODEL_PATH)
        self.recognizer = KaldiRecognizer(self.model, self.RATE)
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()

    def get_location(self):
        geolocator = Nominatim(user_agent="voice_detector_app")
        location = geolocator.geocode("Your location")  # Replace with actual geolocation method
        if location:
            return location.latitude, location.longitude
        else:
            return 0.0, 0.0  # Return default values if location cannot be found

    def send_sms_alert(self, phone_number, latitude, longitude):
        emergency_contacts = [
            "+917066343531",  # Contact 1
            "+918879363714",  # Contact 2
            "+919930404660",  # Contact 3
        ]
        
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            # Message body with location details
            alert_message = (
                f"ALERT: Help word detected three times! Possible emergency situation.\n"
                f"User's Location:\nLatitude: {latitude}, Longitude: {longitude}\n"
                "Please take action immediately!"
            )

            for contact in emergency_contacts:
                message = client.messages.create(
                    body=alert_message,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=contact
                )
                print(f"SMS alert sent to {contact}: {message.sid}")
        except Exception as e:
            print(f"Error sending SMS: {e}")

    def start_detection(self, config):
        """Start voice detection in a separate thread"""
        self.is_running = True
        self.detection_thread = threading.Thread(target=self._detection_loop, args=(config,))
        self.detection_thread.daemon = True  # Thread will be terminated when main program exits
        self.detection_thread.start()

    def stop_detection(self):
        """Stop voice detection"""
        self.is_running = False
        if hasattr(self, 'detection_thread'):
            self.detection_thread.join()

    def _detection_loop(self, config):
        stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        stream.start_stream()
        print(f"Started listening for 'help' for user {config.user.username}...")

        try:
            while self.is_running:
                try:
                    data = stream.read(self.CHUNK, exception_on_overflow=False)
                except IOError:
                    continue

                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").lower()
                    
                    current_time = time.time()
                    
                    if "help" in text:
                        if current_time - self.last_detection_time <= config.time_threshold:
                            self.consecutive_help_count += 1
                        else:
                            self.consecutive_help_count = 1
                        
                        self.last_detection_time = current_time
                        
                        if self.consecutive_help_count >= config.required_repetitions:
                            latitude, longitude = self.get_location()  # Fetch the location
                            self.send_sms_alert(config.phone_number, latitude, longitude)
                            self.consecutive_help_count = 0
                        
        finally:
            stream.stop_stream()
            stream.close()
