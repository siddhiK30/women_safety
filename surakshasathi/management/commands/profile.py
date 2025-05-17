# women_safety/management/commands/create_user_profile.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from surakshasathi.models import Users
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates a user profile for women safety application'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the existing auth.User')
        parser.add_argument('phone_number', type=str, help='Phone number for emergency contact')
        parser.add_argument('--is-helper', action='store_true', help='Flag to mark user as helper')
        parser.add_argument('--email', type=str, help='Email address of the user', default='')
        parser.add_argument('--emergency-contacts', nargs='+', help='List of emergency contact numbers')

    def handle(self, *args, **options):
        username = options['username']
        phone_number = options['phone_number']
        is_helper = options['is_helper']
        email = options['email']
        emergency_contacts = options.get('emergency_contacts', [])

        try:
            # Check if user exists
            user = User.objects.get(username=username)
            
            # Check if profile already exists
            if hasattr(user, 'users'):
                self.stdout.write(
                    self.style.WARNING(f'Profile already exists for {username}')
                )
                return

            # Create new profile
            profile = Users.objects.create(
                user=user,
                phone_number=phone_number,
                is_helper=is_helper,
                email=email,
                created_at=timezone.now(),
                last_active=timezone.now()
            )

            # Add emergency contacts if provided
            if emergency_contacts:
                for contact in emergency_contacts:
                    try:
                        profile.emergency_contacts.create(
                            phone_number=contact,
                            is_primary=emergency_contacts.index(contact) == 0
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Failed to add emergency contact {contact}: {str(e)}')
                        )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created profile for {username}')
            )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Error: User {username} does not exist')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating profile: {str(e)}')
            )