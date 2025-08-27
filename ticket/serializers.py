from rest_framework import serializers
from ticket.models import TicketModel, AnswerTicketModel

class AnswerTicketSerializer(serializers.ModelSerializer):

    class Meta:

        model = AnswerTicketModel
        fields = '__all__'

    def validate_subject(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Subject must be at least 3 characters long.")
        return value

    def validate_message_text(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Message text is too short.")
        return value
        
class TicketSerializer(serializers.ModelSerializer):

    answers = AnswerTicketSerializer(many=True, read_only=True)

    class Meta:

        model = TicketModel
        fields = '__all__'

    def validate_comments(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("The description is too short.")
        return value
