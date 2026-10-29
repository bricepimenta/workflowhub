from django.contrib.auth import get_user_model,authenticate
from rest_framework import generics,status,viewsets,permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Task
from .serializers import TaskSerializer
User=get_user_model()
class RegisterView(APIView):
 permission_classes=[permissions.AllowAny]
 def post(self,request):
  username=request.data.get('username','').strip(); password=request.data.get('password','')
  if not username or len(password)<8: return Response({'detail':'Username and password of 8+ characters required.'},status=400)
  if User.objects.filter(username=username).exists(): return Response({'detail':'Username already exists.'},status=400)
  user=User.objects.create_user(username=username,password=password)
  token,_=Token.objects.get_or_create(user=user)
  return Response({'token':token.key,'username':user.username},status=201)
class LoginView(APIView):
 permission_classes=[permissions.AllowAny]
 def post(self,request):
  user=authenticate(username=request.data.get('username'),password=request.data.get('password'))
  if not user:return Response({'detail':'Invalid credentials.'},status=400)
  token,_=Token.objects.get_or_create(user=user)
  return Response({'token':token.key,'username':user.username})
class LogoutView(APIView):
 def post(self,request):
  request.auth.delete()
  return Response(status=status.HTTP_204_NO_CONTENT)
class TaskViewSet(viewsets.ModelViewSet):
 serializer_class=TaskSerializer
 def get_queryset(self):return Task.objects.filter(owner=self.request.user).order_by('-created_at')
 def perform_create(self,serializer): serializer.save(owner=self.request.user)
