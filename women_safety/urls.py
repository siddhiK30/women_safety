from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('surakshasathi.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    # path('api/', include('surakshasathi.urls')),
]

# Add media URL patterns if in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)