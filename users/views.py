from cgitb import lookup
from django.contrib.auth import get_user_model
from rest_framework import generics, status
# from rest_framework.viewsets import GenericViewSet
# from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import MyTokenObtainPairSerializer, RegisterSerializer, UserSerializer


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
        }, status=status.HTTP_201_CREATED)

class Userlist(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request):
        serializer = UserSerializer(
            User.objects.all(), many=True, context={'request': request}
        )
        return Response(status=status.HTTP_200_OK, data=serializer.data)



class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
