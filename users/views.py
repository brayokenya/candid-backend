from sqlite3 import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from users.serializers import UserSerializer,UserSerializerWithToken,ProfileSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from users.models import Profile




class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # #overriding the validate method
        # data['username'] = self.user.username
        # data['email'] = self.user.email

        #clean up the response 
        #loop through the fields passed in during serialization

        serializer = UserSerializerWithToken(self.user).data
        for k,v in serializer.items():
            data[k] = v

        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['POST'])
def registerUser(request):
    data = request.data
    try:
        user = User.objects.create(
            first_name=data['name'],
            username=data['email'],
            email=data['email'],
            password=make_password(data['password']),
        )
        # Create a profile for the newly registered user
        profile = Profile.objects.create(user=user)

        user_serializer = UserSerializerWithToken(user, many=False)
        profile_serializer = ProfileSerializer(profile, many=False)

         # Combine user and profile data in the response
        response_data = {
            "user": user_serializer.data,
            "profile": profile_serializer.data,
        }

        return Response(response_data)
    
    except IntegrityError as e:
        message = {'detail': 'User with this email already exists'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    
    except KeyError as e:
        message = {'detail': f'Missing field: {e.args[0]}'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
        # Combine user and profile instances in the context to be used by the serializer
    context = {
        'request': request,
        'user': user,
        'profile': profile
    }

    serializer = UserSerializerWithToken(user, data=request.data, context=context)
    data = {}
    if serializer.is_valid():
        # Update the user object using validated data
        user.first_name = serializer.validated_data.get('name', user.first_name)
        user.username = serializer.validated_data.get('email', user.username)
        user.email = serializer.validated_data.get('email', user.email)
        
        # Check if the password field is provided and update the password
        password = serializer.validated_data.get('password')
        if password != '':
            user.password = make_password(password)     
        user.save()    
        profile_data = serializer.validated_data.get('profile')      
        if profile_data:
            profile = user.profile
            profile.location = profile_data.get('location', profile.location)
            profile.interests = profile_data.get('interests', profile.interests)
            profile.image_url = profile_data.get('image_url', profile.image_url)
            profile.save() 
        data['response'] = "Profile updated successfully"
    else:
        data = serializer.errors
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    try:
        profile = user.profile

        # Serialize the User data
        user_serializer = UserSerializer(user, many=False)
        user_data = user_serializer.data
        print(user_data)
        # Manually update the user_data dictionary with profile information
        user_data["profile"] = {
            "id": profile.id,
            "location": profile.location,
            "interests": profile.interests,
            "image_url": request.build_absolute_uri(profile.image_url.url) if profile.image_url else None,
        }
        print(user_data)
        return Response(user_data)
    except Profile.DoesNotExist:
        return Response({"message": "Profile not found"}, status=404)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

