from django.shortcuts import render
from ticket.models import TicketModel
from rest_framework import status
from rest_framework.request import Request
from rest_framework import viewsets
from ticket.serializers import TicketSerializer
# Create your views here.

class TicketViews(viewsets.ModelViewSet):

    queryset = TicketModel.objects.all()
    serializer_class = TicketSerializer