from rest_framework import generics, permissions, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import MyTokenObtainPairSerializer, RegisterSerializer, UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

# Register API view
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user,
            context=self.get_serializer_context()).data,
            "message": "User created successfully. Now log in to get token",
        }, status=201)

class UserDetails(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        token = request.headers['Authorization'].split(' ')[1]
        access_token = AccessToken(token)
        user = User.objects.get(pk=access_token['user_id'])
        message = "Hello, authenticated user!"
        return Response({
            'user': UserSerializer(user,
            context=self.get_serializer_context()).data,
        })

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
