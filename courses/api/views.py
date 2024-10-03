from rest_framework import generics
from ..models import Subject
from .serializers import SubjectSerializer


'''Generic View Purpose to simplify the creation of API for 
   Retriving,Creating,Updating or deleting 
'''

class SubjectListView(generics.ListAPIView):
    # Retrive all Subjects object
    queryset = Subject.objects.all()
    # spcific the SubjectSerializer to serialize the subject object
    serializer_class = SubjectSerializer

class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Subject.objects.all()
    # Uses primary key(pk) URL pattern to retrieve specific object
    serializer_class = SubjectSerializer

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
# it handles converting python data stucture into json format automatically
from rest_framework.response import Response
from ..models import Course
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

'''custom Request and Response object handle exceptions using APIException'''

class CourseEnrollView(APIView):
    # users will be identifying by the credentials set in the authorization header of the http request
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    # handles http post method
    def post(self, request, pk, format=None):
        course = get_object_or_404(Course, pk=pk)
        course.students.add(request.user)
        return Response({'enrolled': True}) 

from rest_framework import viewsets
from rest_framework.decorators import action
from .serializers import CourseSerializer,CourseWithContentsSerializer
from .permissions import IsEnrolled

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    @action(detail=True,methods=['post'],authentication_classes=[BasicAuthentication],
            permission_classes=[IsAuthenticated])
    def enroll(self, request, *args, **kwargs):
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enrolled': True})
    
    @action(detail=True,methods=['get'],serializer_class=CourseWithContentsSerializer,
            authentication_classes=[BasicAuthentication],permission_classes=[IsAuthenticated, IsEnrolled])
    def contents(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)