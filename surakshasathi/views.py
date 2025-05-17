from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from .models import SafetySession, TrustedContact, LocationShare, SafetyCategory, SafetyTip
from django.contrib import messages
import requests
import logging
from django.http import JsonResponse
import json
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MarkerSerializer
from .models import Marker
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import SafetyIncident
from math import radians, sin, cos, sqrt, atan2
from .models import Users
from django.contrib.auth.models import User
from math import radians, sin, cos, sqrt, atan2
from .models import Users

import uuid
from twilio.rest import Client
from django.conf import settings
import googlemaps


# API route to fetch all markers
def get_markers(request):
    markers = Marker.objects.all().values('lat', 'lng')
    print(markers)  # Check if the correct markers are being returned
    return JsonResponse(list(markers), safe=False)


# API route to add a new marker
import json
from django.http import JsonResponse

def add_marker(request):
    if request.method == "POST":
        data = json.loads(request.body)
        lat = data.get('lat')
        lng = data.get('lng')

        print(f"Received marker: lat={lat}, lng={lng}")  # Debug log to check the received data

        # Save the marker to the database
        marker = Marker.objects.create(lat=lat, lng=lng)
        return JsonResponse({'id': marker.id, 'lat': lat, 'lng': lng})


def index(request):
    markers = Marker.objects.all()  # Fetch all markers from the database
    markers_data = list(markers.values('lat', 'lng'))  # Convert queryset to list of dicts
    return render(request, 'area_flag.html', {'markers': markers_data})

class MarkerListCreateView(APIView):
    def get(self, request):
        markers = Marker.objects.all()
        serializer = MarkerSerializer(markers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MarkerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MarkerUpdateView(APIView):
    def put(self, request, pk):
        try:
            marker = Marker.objects.get(pk=pk)
            serializer = MarkerSerializer(marker, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Marker.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username Already Used!')
                return redirect('signup')
            
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Already have an account for this Email!')
                return redirect('signup')
            
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                # startup = Startup(user=user, name=username, email=email)
                # startup.save()
                return redirect('login')
        else:
            messages.info(request, 'Password Not The Same!')
            return redirect('signup')
        
    else:    
        return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Credentials Invalid!')
            return redirect('login')
    else:
        return render(request, 'login.html')  
    

def videocall_view(request):
    return render(request, 'videocall.html')  # Correct relative path
def voice_view(request):
    return render(request, 'voicecall.html') 
def video_view(request):
    return render(request, 'video.html') 



def badges(request):
    context = {
        'count': MarkerCount.get_count(),
        'incident_count' : IncidentMarkerCount.get_count()
    }
    return render(request, 'badge.html', context)


def sessions(request):
    sessions = SafetySession.objects.all()
    return render(request, 'sessions.html', {'sessions': sessions})    


# Initialize logger
logger = logging.getLogger(__name__)

def geocode_address(address):
    if not address:
        return None, None

    try:
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'in',  # Restrict search to India
        }
        headers = {'User-Agent': 'SurakshaSathi/1.0'}
        response = requests.get(base_url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
        
        # Log error when no result is found
        logger.error(f"No geocoding result for address: {address}")
        return None, None
    except Exception as e:
        # Log exception for debugging
        logger.error(f"Geocoding error: {e}")
        return None, None


def session_map(request, session_id):
    session = get_object_or_404(SafetySession, id=session_id)
    
    # Check if session has a location
    if not session.location:
        return render(request, 'session_map.html', {
            'session': session,
            'error': 'No valid location available for this session.'
        })
    
    # Get coordinates using geocode_address
    lat, lng = geocode_address(session.location)
    
    if lat is None or lng is None:
        # If geocoding fails, render with an error message
        return render(request, 'session_map.html', {
            'session': session,
            'error': 'Unable to geocode the session location.'
        })

    context = {
        'session': session,
        'session_lat': lat,
        'session_lng': lng
    }
    return render(request, 'session_map.html', context)

def safety_tips(request):
    return render(request, 'safety_tips.html')

def upload(request):
    return render(request, 'upload.html')

def area_flag(request):
    return render(request, 'area_flag.html')

   
def anomoly(request):
    return render(request, 'anomoly.html')

def offline(request):
    return render(request, 'mumbai_map.html')

# def chatbot_api(request):
#     if request.method == 'POST':
#         user_message = request.POST.get('message')
#         # Define your prompt for OpenAI GPT
#         prompt = """You are a safety assistant for women. Provide clear, concise, and actionable safety advice. Ensure your answers are friendly, empathetic, and professional. Also if they feel stressed make them feel relief give them solutions. Your response should not be bigger than 5 sentence but it can be smaller upto one sentence depeneds on question. Answer the following question based on information provided earlier: 
#             """ 
        
#         prompt += user_message

#         api_key = 'AIzaSyA1fQnq8k8ckP5WEyF97kDmLiAGnVhPKz4'

#         try:
#             genai.configure(api_key=api_key)
#             model = genai.GenerativeModel("gemini-1.5-flash")
#             response = model.generate_content(prompt)
#             reply = response.text

#             return JsonResponse({'reply': reply})

#         except Exception as e:
#             return JsonResponse({'reply': f'An error occurred: {str(e)}'}) 
# logger = logging.getLogger(__name__)


import requests
from django.http import JsonResponse
from django.conf import settings
import logging
import json
from math import radians, sin, cos, sqrt, atan2

logger = logging.getLogger(__name__)

def get_address_from_coordinates(lat, lon):
    """Reverse geocode coordinates using Nominatim API"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {'User-Agent': 'SafetyTrails/1.0'}  # Required by Nominatim
        response = requests.get(url, headers=headers)
        data = response.json()
        return data.get('display_name', '')
    except Exception as e:
        logger.error(f"Error in reverse geocoding: {str(e)}")
        return None

def get_nearby_services(lat, lon):
    """Get nearby police stations and hospitals using Overpass API"""
    try:
        # Search within 5km radius
        radius = 5000
        overpass_url = "https://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="police"](around:{radius},{lat},{lon});
          way["amenity"="police"](around:{radius},{lat},{lon});
          node["amenity"="hospital"](around:{radius},{lat},{lon});
          way["amenity"="hospital"](around:{radius},{lat},{lon});
        );
        out body;
        >;
        out skel qt;
        """
        response = requests.post(overpass_url, data=overpass_query)
        data = response.json()
        
        services = []
        for element in data.get('elements', []):
            if element.get('tags'):
                service = {
                    'type': element['tags'].get('amenity'),
                    'name': element['tags'].get('name', 'Unnamed'),
                    'lat': element.get('lat', 0),
                    'lon': element.get('lon', 0)
                }
                services.append(service)
        
        return services
    except Exception as e:
        logger.error(f"Error fetching nearby services: {str(e)}")
        return []

def generate_safety_response(address, nearby_services):
    """Generate a context-aware safety response"""
    response = f"📍 Your current location: {address}\n\n"
    response += "🚨 Nearby Emergency Services:\n"
    
    police_stations = [s for s in nearby_services if s['type'] == 'police']
    hospitals = [s for s in nearby_services if s['type'] == 'hospital']
    
    if police_stations:
        response += "\n👮 Police Stations:\n"
        for station in police_stations[:3]:  # Show top 3
            response += f"- {station['name']}\n"
    
    if hospitals:
        response += "\n🏥 Hospitals:\n"
        for hospital in hospitals[:3]:  # Show top 3
            response += f"- {hospital['name']}\n"
    
    response += "\n🔒 Safety Tips for Your Area:\n"
    response += "1. Keep emergency numbers saved\n"
    response += "2. Share your location with trusted contacts\n"
    response += "3. Stay in well-lit areas\n"
    response += "4. Use the SOS button for immediate help"
    
    return response

def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            lat = data.get('latitude')
            lon = data.get('longitude')

            # Keywords related to women's safety
            safety_keywords = ['safe', 'safety', 'help', 'danger', 'unsafe', 'feeling unsafe', 'women safety', 'self-defense', 'harassment', 'abuse']
            is_safety_query = any(keyword in user_message.lower() for keyword in safety_keywords)

            if lat and lon:
                if is_safety_query:
                    # Location-based safety response
                    address = get_address_from_coordinates(lat, lon)
                    nearby_services = get_nearby_services(lat, lon)
                    response = generate_safety_response(address, nearby_services)
                else:
                    # Normal conversation response when location is available
                    prompt = f"You're a safety assistant for women. Respond to the following query:\n{user_message}"
                    
                    api_key = 'AIzaSyA1fQnq8k8ckP5WEyF97kDmLiAGnVhPKz4'  # Replace with your actual API key
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(prompt)
                    response = response.text
            else:
                if is_safety_query:
                    # Fallback: General advice when location is not available
                    response = "I understand you feel unsafe. Here are some general safety tips for women:"
                    response += "\n1. Always be aware of your surroundings."
                    response += "\n2. Avoid walking alone at night in isolated areas."
                    response += "\n3. Keep your phone charged and with you at all times."
                    response += "\n4. Share your location with trusted friends or family."
                    response += "\n5. Know the emergency numbers in your area."
                    response += "\n6. Carry a personal alarm or pepper spray for self-defense."
                else:
                    # Generic conversation response when location is not available
                    prompt = f"You're a friendly safety assistant for women. Respond to the following query:\n{user_message}"
                    
                    api_key = 'AIzaSyA1fQnq8k8ckP5WEyF97kDmLiAGnVhPKz4'  # Replace with your actual API key
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(prompt)
                    response = response.text

            return JsonResponse({'reply': response})

        except Exception as e:
            logger.error(f"Error in chatbot API: {str(e)}")
            return JsonResponse({'reply': 'Sorry, I encountered an error. Please try again.'})

    return JsonResponse({'reply': 'Invalid request method'})



def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def get_nearby_users(current_user, max_distance=5):
    """Get list of users within specified distance"""
    if not current_user.latitude or not current_user.longitude:
        return []
        
    users = Users.objects.exclude(user=current_user.user).filter(is_active=True)
    nearby_users = []
    
    for user in users:
        if user.latitude and user.longitude:
            distance = calculate_distance(
                current_user.latitude, 
                current_user.longitude,
                user.latitude, 
                user.longitude
            )
            if distance <= max_distance:
                nearby_users.append({
                    'user': user,
                    'name': user.name,
                    'distance': round(distance, 1)
                })
    
    return sorted(nearby_users, key=lambda x: x['distance'])

from voice_detector.utils import VoiceDetector
from voice_detector.models import UserAlertConfig

@login_required
def home_view(request):
    try:
        # Initialize voice detection for the user
        config, created = UserAlertConfig.objects.get_or_create(
            user=request.user,
            defaults={
                'phone_number': request.user.profile.phone_number if hasattr(request.user, 'profile') else '',
                'required_repetitions': 3,
                'time_threshold': 5
            }
        )
        
        # Start voice detection
        detector = VoiceDetector()
        detector.start_detection(config)

        # Your existing code
        current_user_profile = Users.objects.get(user=request.user)
        nearby_users = get_nearby_users(current_user_profile)
        
        context = {
            'current_user_name': current_user_profile.name,
            'current_user_location': {
                'latitude': current_user_profile.latitude,
                'longitude': current_user_profile.longitude
            },
            'nearby_users': nearby_users,
            'has_location': bool(current_user_profile.latitude and current_user_profile.longitude)
        }
        
        return render(request, 'home.html', context)
        
    except Users.DoesNotExist:
        return render(request, 'home.html', {
            'error_message': "Please complete your profile to see nearby users.",
            'nearby_users': [],
            'has_location': False
        })

@csrf_exempt
@login_required
def send_emergency_alert(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        location = data.get('location')
        requester = request.user
        requester_profile = Users.objects.get(user=requester)
        
        if not location or 'latitude' not in location or 'longitude' not in location:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid location data'
            }, status=400)
            
        # Update requester's location
        requester_profile.latitude = location['latitude']
        requester_profile.longitude = location['longitude']
        requester_profile.save()
        
        # Get nearby users
        nearby_users = get_nearby_users(requester_profile)
        location_url = f"https://www.google.com/maps?q={location['latitude']},{location['longitude']}"
        
        # Initialize Twilio and track messages
        twilio = TwilioService()
        message_attempts = []
        
        # Send alerts to nearby users
        for user_data in nearby_users:
            nearby_user = user_data['user']
            try:
                if nearby_user.phone_number:
                    success, msg_id = twilio.send_emergency_sms(
                        to_number=nearby_user.phone_number,
                        requester_name=requester.username,
                        location_url=location_url,
                        message_type='nearby user',
                        
                    )
                    message_attempts.append({
                        'user_name': nearby_user.name,
                        'distance': user_data['distance'],
                        'success': success,
                        'message_id': msg_id
                    })
            except Exception as e:
                logger.error(f"Error sending alert to nearby user {nearby_user.name}: {str(e)}")
                message_attempts.append({
                    'user_name': nearby_user.name,
                    'distance': user_data['distance'],
                    'success': False,
                    'error': str(e)
                })

        # Send alerts to trusted contacts
        trusted_contacts = TrustedContact.objects.filter(user=requester)
        for contact in trusted_contacts:
            try:
                success, msg_id = twilio.send_emergency_sms(
                    to_number=contact.phone,
                    requester_name=requester.username,
                    location_url=location_url,
                    message_type='trusted_contact'
                )
                message_attempts.append({
                    'contact_name': contact.name,
                    'type': 'trusted_contact',
                    'success': success,
                    'message_id': msg_id
                })
            except Exception as e:
                logger.error(f"Error sending alert to trusted contact {contact.name}: {str(e)}")
                message_attempts.append({
                    'contact_name': contact.name,
                    'type': 'trusted_contact',
                    'success': False,
                    'error': str(e)
                })

        return JsonResponse({
            'status': 'success',
            'message': f"Emergency alerts sent to {len(message_attempts)} recipients",
            'details': {
                'nearby_users_count': len(nearby_users),
                'trusted_contacts_count': len(trusted_contacts),
                'message_attempts': message_attempts
            }
        })

    except Exception as e:
        logger.error(f"Emergency alert error: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def trusted_contacts_page(request):
    return render(request, 'trusted_contacts.html')

@login_required
@require_http_methods(["GET", "POST"])
def trusted_contacts_api(request):
    if request.method == "GET":
        contacts = TrustedContact.objects.filter(user=request.user).order_by('created_at')
        return JsonResponse([{
            'id': contact.id,
            'name': contact.name,
            'phone': contact.phone,
            'relationship': contact.relationship
        } for contact in contacts], safe=False)
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            contact = TrustedContact(
                user=request.user,
                name=data.get('name', '').strip(),
                phone=data.get('phone', '').strip(),
                relationship=data.get('relationship', '').strip()
            )
            contact.save()
            return JsonResponse({
                'id': contact.id,
                'name': contact.name,
                'phone': contact.phone,
                'relationship': contact.relationship
            }, status=201)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["DELETE"])
def delete_contact(request, contact_id):
    try:
        contact = TrustedContact.objects.filter(
            user=request.user,
            id=contact_id
        ).first()
        
        if not contact:
            return JsonResponse({'error': 'Contact not found'}, status=404)
        
        contact.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_incidents(request):
    """API endpoint to get all incidents"""
    incidents = SafetyIncident.objects.all().order_by('-created_at')
    data = []
    for incident in incidents:
        data.append({
            'id': incident.id,
            'title': incident.title,
            'description': incident.description,
            'latitude': incident.latitude,
            'longitude': incident.longitude,
            'media_url': incident.media.url if incident.media else None,
            'created_at': incident.created_at.isoformat()
        })
    return JsonResponse(data, safe=False)

def get_incident_details(request, incident_id):
    """API endpoint to get details of a specific incident"""
    try:
        incident = SafetyIncident.objects.get(id=incident_id)
        data = {
            'id': incident.id,
            'title': incident.title,
            'description': incident.description,
            'latitude': incident.latitude,
            'longitude': incident.longitude,
            'media_url': incident.media.url if incident.media else None,
            'created_at': incident.created_at.isoformat()
        }
        return JsonResponse(data)
    except SafetyIncident.DoesNotExist:
        return JsonResponse({'error': 'Incident not found'}, status=404)

@csrf_exempt
def create_incident(request):
    """API endpoint to create a new incident"""
    incidentncount =  IncidentMarkerCount.increment()
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        title = request.POST.get('title')
        description = request.POST.get('description')
        location_coords = json.loads(request.POST.get('location_coords'))
        media_file = request.FILES.get('media')

        if not all([title, description, location_coords]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Save the incident
        incident = SafetyIncident.objects.create(
            title=title,
            description=description,
            latitude=location_coords[1],
            longitude=location_coords[0],
            media=media_file
        )

        # Update or create marker as unsafe
        Marker.objects.update_or_create(
            lat=location_coords[1],
            lng=location_coords[0],
            defaults={'safety_status': 'unsafe'}
        )

        return JsonResponse({
            'id': incident.id,
            'message': 'Incident created successfully, and area marked as unsafe.'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# In your views.py
from django.http import JsonResponse

def send_help_request(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_name = data.get('name', '')
            # Process the help request, e.g., send an email or log it
            # Respond with success
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

from twilio.rest import Client
from django.conf import settings
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Users, TrustedContact
from .services import TwilioService

# @login_required
# @require_http_methods(["POST"])
# def update_location(request):
#     try:
#         data = json.loads(request.body)
#         location = LocationShare.objects.create(
#             user=request.user,
#             latitude=data['latitude'],
#             longitude=data['longitude'],
#             timestamp=data['timestamp']
#         )
        
#         # Get user's trusted contacts
#         trusted_contacts = TrustedContact.objects.filter(user=request.user)
        
#         # Notify trusted contacts through WebSocket
#         channel_layer = get_channel_layer()
#         for contact in trusted_contacts:
#             async_to_sync(channel_layer.group_send)(
#                 f"location_updates_{contact.id}",
#                 {
#                     "type": "location_update",
#                     "message": {
#                         "latitude": data['latitude'],
#                         "longitude": data['longitude'],
#                         "timestamp": data['timestamp'],
#                         "user": request.user.username
#                     }
#                 }
#             )
        
#         return JsonResponse({"status": "success"})
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=400)

# @login_required
# @require_http_methods(["POST"])
# def stop_sharing(request):
#     try:
#         # Update sharing status
#         LocationShare.objects.filter(user=request.user, active=True).update(active=False)
        
#         # Notify trusted contacts that sharing has stopped
#         trusted_contacts = TrustedContact.objects.filter(user=request.user)
#         channel_layer = get_channel_layer()
        
#         for contact in trusted_contacts:
#             async_to_sync(channel_layer.group_send)(
#                 f"location_updates_{contact.id}",
#                 {
#                     "type": "sharing_stopped",
#                     "message": {
#                         "user": request.user.username
#                     }
#                 }
#             )
        
#         return JsonResponse({"status": "success"})
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
@csrf_exempt
def send_sos(request):
    if request.method == "POST":
        try:
            # Load location data from request
            data = json.loads(request.body)
            latitude = data["latitude"]
            longitude = data["longitude"]

            # Define user's emergency contacts
            emergency_contacts = [
                "+917066343531",  # Contact 1
                "+918879363714",  # Contact 2
                "+919930404660",  # Contact 3
            ]

            # Twilio credentials
            account_sid = "ACf204394952d87fc728ead2d682620b32"
            auth_token = "0a37c5f1e46ace5872fa1a444b5883a0"
            client = Client(account_sid, auth_token)

            # Message body with location
            message_body = (
                f"Emergency! The user needs help. Location: "
                f"https://www.google.com/maps?q={latitude},{longitude}"
            )

            # Send SMS to all emergency contacts
            for contact in emergency_contacts:
                client.messages.create(
                    body=message_body,
                    from_="+16084296876",
                    to=contact,
                )

            return JsonResponse({"message": "SOS messages sent successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method."}, status=400)

@csrf_exempt
def make_call(request):
    if request.method == "POST":
        # Twilio credentials
        account_sid = 'ACf204394952d87fc728ead2d682620b32'
        auth_token = '0a37c5f1e46ace5872fa1a444b5883a0'
        client = Client(account_sid, auth_token)

        # Call parameters
        to_number = '+919930404660'
        from_number = '+16084296876'
        call_url = "https://yourdomain.com/twiml_response/"  # Update with your endpoint

        try:
            call = client.calls.create(
                to=to_number,
                from_=from_number,
                url=call_url
            )
            return JsonResponse({"status": "success", "call_sid": call.sid})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request"})

from twilio.twiml.voice_response import VoiceResponse
from django.http import HttpResponse
# View to serve TwiML
def twiml_response(request):
    response = VoiceResponse()
    response.say("This is an emergency call. I need your help. Please come here.", voice='alice', language='en-US')
    return HttpResponse(str(response), content_type="application/xml")
    


from django.db import models  
class MarkerCount(models.Model):
    count = models.IntegerField(default=0)
    
    @classmethod
    def increment(cls):
        counter, created = cls.objects.get_or_create(id=1)
        counter.count += 1
        counter.save()
        return counter.count
        
    @classmethod
    def get_count(cls):
        counter, created = cls.objects.get_or_create(id=1)
        return counter.count

class IncidentMarkerCount(models.Model):
    countincident = models.IntegerField(default=0)
    
    @classmethod
    def increment(cls):
        counter, created = cls.objects.get_or_create(id=1)
        counter.countincident += 1
        counter.save()
        return counter.countincident
        
    @classmethod
    def get_count(cls):
        counter, created = cls.objects.get_or_create(id=1)
        return counter.countincident
    
# Initialize Twilio client
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

# Initialize Google Maps client
gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

@login_required
@csrf_exempt
def share_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            # Generate unique share ID if not exists
            location_share = LocationShare.objects.filter(
                user=request.user,
                is_active=True
            ).first()
            
            if not location_share:
                share_id = str(uuid.uuid4())
                location_share = LocationShare.objects.create(
                    user=request.user,
                    latitude=latitude,
                    longitude=longitude,
                    share_id=share_id
                )
                
                # Send location link via Twilio to trusted contacts
                location_link = f"{settings.SITE_URL}/track/{share_id}"
                trusted_contacts = TrustedContact.objects.filter(user=request.user)
                
                for contact in trusted_contacts:
                    message = twilio_client.messages.create(
                        body=f"{request.user.get_full_name()} is sharing their location with you: {location_link}",
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=contact.phone_number
                    )
            else:
                location_share.latitude = latitude
                location_share.longitude = longitude
                location_share.save()
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
@csrf_exempt
def stop_location_sharing(request):
    if request.method == 'POST':
        LocationShare.objects.filter(
            user=request.user,
            is_active=True
        ).update(is_active=False)
        
        # Notify trusted contacts that sharing has stopped
        trusted_contacts = TrustedContact.objects.filter(user=request.user)
        for contact in trusted_contacts:
            message = twilio_client.messages.create(
                body=f"{request.user.get_full_name()} has stopped sharing their location.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=contact.phone_number
            )
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def track_location(request, share_id):
    try:
        # Retrieve the active location share using the share_id
        location_share = LocationShare.objects.filter(
            share_id=share_id,
            is_active=True
        ).first()

        if location_share:
            # Return location details
            return JsonResponse({
                'status': 'success',
                'user': location_share.user.username,
                'latitude': float(location_share.latitude),
                'longitude': float(location_share.longitude),
                'timestamp': location_share.timestamp,
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Location not found or sharing has stopped.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def safety_tips(request):
    categories = SafetyCategory.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'safety_tips.html', context)

def get_tips(request, category_slug):
    try:
        category = SafetyCategory.objects.get(slug=category_slug)
        tips = SafetyTip.objects.filter(category=category)
        tips_data = [{
            'title': tip.title,
            'description': tip.description,
            'tags': tip.get_tags_list()
        } for tip in tips]
        return JsonResponse({'tips': tips_data})
    except SafetyCategory.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)

def search_tips(request):
    query = request.GET.get('q', '')
    tips = SafetyTip.objects.filter(
        models.Q(title__icontains=query) |
        models.Q(description__icontains=query) |
        models.Q(tags__icontains=query)
    )
    tips_data = [{
        'title': tip.title,
        'description': tip.description,
        'tags': tip.get_tags_list(),
        'category': tip.category.name
    } for tip in tips]
    return JsonResponse({'tips': tips_data})