import logging
from twilio.rest import Client
from django.conf import settings

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.from_number = settings.TWILIO_PHONE_NUMBER

    def send_emergency_sms(self, to_number, requester_name, location_url, message_type):
        try:
            # Format the message based on type
            if message_type == 'helper':
                message_body = (
                    f"EMERGENCY ALERT: {requester_name} needs immediate assistance! "
                    f"Their location: {location_url}"
                )
            else:  # trusted_contact
                message_body = (
                    f"EMERGENCY ALERT: Your trusted contact {requester_name} "
                    f"has triggered an emergency alert. Their location: {location_url}"
                )

            # Log the attempt
            logger.info(f"Attempting to send SMS to {to_number}")

            # Send the message
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=to_number
            )

            logger.info(f"SMS sent successfully to {to_number}. Message ID: {message.sid}")
            return True, message.sid

        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {str(e)}")
            return False, None