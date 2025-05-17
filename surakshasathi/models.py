from django.db import models
from django.contrib.auth.models import User    
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid

class Users(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    latitude = models.FloatField(null=True, blank=True)  # Add latitude
    longitude = models.FloatField(null=True, blank=True)  # Add longitude
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    # Add more fields as necessary

    def __str__(self):
        return self.name
    def __str__(self):
        return f"{self.user.username} - {'Active' if self.is_active else 'Inactive'}"

    

class SafetySession(models.Model):
    SESSION_TYPE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    session_type = models.CharField(max_length=10, choices=SESSION_TYPE_CHOICES)
    schedule = models.CharField(max_length=255)  # e.g., "Every Saturday, 10:00 AM - 12:00 PM"
    contact_number = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    def get_full_address(self):
        """Returns a complete address string for geocoding"""
        parts = [self.location]
        if self.street_address:
            parts.append(self.street_address)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.pincode:
            parts.append(self.pincode)
        return ', '.join(filter(None, parts))


class Marker(models.Model):
    SAFETY_CHOICES = [
        ('safe', 'Safe'),
        ('moderate', 'Moderate'),
        ('unsafe', 'Unsafe'),
    ]
    
    lat = models.FloatField()
    lng = models.FloatField()
    safety_status = models.CharField(
        max_length=10, 
        choices=SAFETY_CHOICES,
        default='moderate'  # Setting default value as 'moderate'
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.safety_status} marker at ({self.lat}, {self.lng})"
    

class TrustedContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    relationship = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        # Remove the constraint from Meta and handle it in save method

    def clean(self):
        if not self.pk:  # If this is a new contact
            existing_contacts = TrustedContact.objects.filter(user=self.user)
            if existing_contacts.count() >= 3:
                raise ValidationError('Maximum limit of 3 contacts reached.')
            # Check for duplicate phone number
            if existing_contacts.filter(phone=self.phone).exists():
                raise ValidationError('This phone number is already registered as a trusted contact.')
        
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.relationship}"

class SafetyIncident(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    media = models.ImageField(upload_to='incidents/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
class LocationShare(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    share_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)

    def __str__(self):
        return f"{self.user.username}'s location at {self.timestamp}"
    


class SafetyCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.TextField(help_text="SVG icon code")
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Safety Categories"

    def __str__(self):
        return self.name

class SafetyTip(models.Model):
    category = models.ForeignKey(SafetyCategory, on_delete=models.CASCADE, related_name='tips')
    title = models.CharField(max_length=200)
    description = models.TextField()
    tags = models.CharField(max_length=200, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',')]