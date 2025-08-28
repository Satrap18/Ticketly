from django.shortcuts import render
from ticket.models import TicketModel, AnswerTicketModel
from rest_framework import status
from rest_framework.request import Request
from rest_framework import viewsets
from ticket.serializers import TicketSerializer, AnswerTicketSerializer
# Create your views here.

class TicketViewSet(viewsets.ModelViewSet):

    queryset = TicketModel.objects.all()
    serializer_class = TicketSerializer


class AnswerTicketViewSet(viewsets.ModelViewSet):

    queryset = AnswerTicketModel.objects.all()
    serializer_class = AnswerTicketSerializer