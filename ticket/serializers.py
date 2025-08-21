from rest_framework import serializers
from ticket.models import TicketModel

class TicketSerializer(serializers.ModelSerializer):

    class Meta:

        model = TicketModel
        fields = '__all__'
