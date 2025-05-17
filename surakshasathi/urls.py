from django.urls import path
from . import views
from .views import make_call, twiml_response
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    # path('kyc/', views.kyc_view, name='kyc'),
    path('home/', views.home_view, name='home'),
    path('home/video.html', views.video_view, name='video'),
    path('home/videocall.html', views.videocall_view, name='videocall'),
    path('home/voicecall.html', views.voice_view, name='voice'),
    path('home/sessions.html', views.sessions, name='sessions'),
    path('home/badge.html', views.badges, name='badges'),
    path('home/mumbai_map.html', views.offline, name='offline'),
    path('make-call/', views.make_call, name='make_call'),
    path('session/<int:session_id>/map/', views.session_map, name='session_map'),
    path('home/safety-tips/', views.safety_tips, name='safety_tips'),
    path('home/upload/', views.upload, name='upload'),
    path('home/area_flag/', views.area_flag, name='area_flag'),
    path('home/anomoly/', views.anomoly, name='anomoly'),
    path('chatbot-api/', views.chatbot_api, name='chatbot_api'),
    # path('nearby-users/', views.nearby_users, name='nearby_users'),
    path('api/markers/', views.MarkerListCreateView.as_view(), name='marker-list-create'),
    path('api/markers/<int:pk>/', views.MarkerUpdateView.as_view(), name='marker-update'),
    path('twiml_response/', twiml_response, name='twiml_response'),
    path('api/send-emergency-alert/', views.send_emergency_alert, name='send_emergency_alert'),
    
    path('trusted-contacts/', views.trusted_contacts_page, name='trusted_contacts'),
    path('api/trusted-contacts/', views.trusted_contacts_api, name='trusted_contacts_api'),
    path('api/trusted-contacts/<int:contact_id>/', views.delete_contact, name='delete_contact'),

    # path('api/location/update/', views.update_location, name='update_location'),
    # path('api/location/stop-sharing/', views.stop_sharing, name='stop_sharing'),

    path("send-sos/", views.send_sos, name="send_sos"),

    path('api/send-emergency-alert/', views.send_emergency_alert, name='send_emergency_alert'),

    path('share-location/', views.share_location, name='share_location'),
    path('stop-location-sharing/', views.stop_location_sharing, name='stop_location_sharing'),
    path('track/<str:share_id>/', views.track_location, name='track_location'),

    path('safety-tips/', views.safety_tips, name='safety_tips'),
    path('api/tips/<slug:category_slug>/', views.get_tips, name='get_tips'),
    path('api/tips/search/', views.search_tips, name='search_tips'),

    path('api/incidents/', views.get_incidents, name='get_incidents'),
    path('api/incidents/create/', views.create_incident, name='create_incident'),
    path('api/incidents/<int:incident_id>/', views.get_incident_details, name='get_incident_details'),
]