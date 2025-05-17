from django.contrib import admin
from .models import SafetySession, Marker, SafetyCategory, SafetyTip
from django.contrib.admin import ModelAdmin
from django.core.exceptions import ValidationError

@admin.register(SafetySession)
class SafetySessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'session_type', 'price', 'schedule')
    search_fields = ('name', 'session_type')
    list_filter = ('session_type',)
from django.contrib import admin
from .models import Users

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number']
    search_fields = ['user__username', 'phone_number']

@admin.register(Marker)
class MarkerAdmin(ModelAdmin):
    list_display = ['id', 'lat', 'lng', 'safety_status', 'created_at']
    list_filter = ['safety_status', 'created_at']
    search_fields = ['id', 'safety_status']
    date_hierarchy = 'created_at'
    
    # Remove readonly_fields to allow editing
    fields = ['lat', 'lng', 'safety_status']
    
    # Allow adding permission for admin
    def has_add_permission(self, request):
        return request.user.is_superuser
        
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
        
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    # Optional: Add form validation
    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('lat')
        lng = cleaned_data.get('lng')
        
        # Validate latitude range
        if lat and (lat < -90 or lat > 90):
            raise ValidationError({'lat': 'Latitude must be between -90 and 90 degrees'})
            
        # Validate longitude range
        if lng and (lng < -180 or lng > 180):
            raise ValidationError({'lng': 'Longitude must be between -180 and 180 degrees'})
            
        return cleaned_data    
    
from .models import SafetyCategory, SafetyTip

@admin.register(SafetyCategory)
class SafetyCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(SafetyTip)
class SafetyTipAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description', 'tags')