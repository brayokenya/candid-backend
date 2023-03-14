from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class UserSerializer(serializers.ModelSerializer):
    #creating custom fields
    name = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id','_id','username','email', 'name', 'isAdmin']
    
    #create a custom serialization method name that stores 
    # both the first name and last name without customizing the user model and updating the db
    #self is the serializer, obj is the User model
    def get__id(self, obj):
        return obj.id
    
    def get_isAdmin(self,obj):
        return obj.is_staff
    
    def get_name(self, obj):
        name = obj.first_name
        #incase the user doesn't have a name use email
        if name == '':
            name = obj.email

        return name
    
class UserSerializerWithToken(UserSerializer): 
    token = serializers.SerializerMethodField(read_only=True)
    

    class Meta:
        model = User
        fields = ['id','_id','username','email', 'name', 'isAdmin','token']
    
    #generate another token with the initial response during serialization after registration
    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)