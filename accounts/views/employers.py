from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import  IsAuthenticated
from accounts import models
from accounts.models import  EmployerProfile
from accounts.models.rating import Rating
from accounts.permissions import IsEmployerOnly
from accounts.serializers.profile import EmployerProfileSerializer
import logging
from accounts.serializers.rating import RatingSerializer
from accounts.utils.profile_notify import notify_managers_about_profile
 


logger = logging.getLogger(__name__)

class EmployerProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsEmployerOnly]

    def get_object(self, user):
        return EmployerProfile.objects.filter(user=user).first()

    @action(detail=False, methods=['post'], url_path='create')
    def create_profile(self, request):
        serializer = EmployerProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile = EmployerProfile.objects.create_profile(user=request.user, **serializer.validated_data)
            notify_managers_about_profile(user_type="employer", user_email=request.user.email)
            return Response(EmployerProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get'], url_path='me')
    def retrieve_profile(self, request):
        profile = self.get_object(request.user)
        if not profile:
            return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(EmployerProfileSerializer(profile).data)

    @action(detail=False, methods=['put'], url_path='update')
    def update_profile(self, request):
        profile = self.get_object(request.user)
        if not profile:
            return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployerProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            profile = EmployerProfile.objects.update_profile(profile, **serializer.validated_data)
            notify_managers_about_profile(user_type="employer", user_email=request.user.email)
            return Response(EmployerProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], url_path='delete')
    def delete_profile(self, request):
        profile = self.get_object(request.user)
        if profile:
            EmployerProfile.objects.delete_profile(profile)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
    

class EmployerRatingViewSet(viewsets.ViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Authenticated user’s own ratings
        return Rating.objects.filter(rater=self.request.user)
    

    @action(detail=False, methods=['get'], url_path='employer/(?P<pk>[^/.]+)/ratings')
    def employer_ratings(self, request, pk=None):
        employer = get_object_or_404(EmployerProfile, pk=pk)
        ratings = Rating.objects.filter(employer=employer)
        serializer = self.get_serializer(ratings, many=True)
        avg = round(ratings.aggregate(models.Avg('score'))['score__avg'] or 0.0, 2)
        count = ratings.count()
        return Response({
            "average_rating": avg,
            "rating_count": count,
            "ratings": serializer.data
        })
