from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializers import GoogleSignInSerializer
from rest_framework import status


# Create your views here.
class GoogleSignInView(GenericAPIView):
    serializer_class = GoogleSignInSerializer

    def post(self, request):
        serializer = self.get_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=((serializer.validated_data)['access_token'])
        return Response(data, status=status.HTTP_200_OK)