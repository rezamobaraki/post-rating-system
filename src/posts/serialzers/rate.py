from rest_framework import serializers

from posts.enums import RateScoreEnum
from posts.fraud_detection import is_fraudulent_activity
from posts.models import Rate
from posts.services.commands import update_or_create_rate



class RateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    score = serializers.IntegerField(
        required=True, min_value=RateScoreEnum.ZERO_STARS, max_value=RateScoreEnum.FIVE_STARS
    )

    def validate(self, attrs):
        if is_fraudulent_activity(attrs['user'], attrs['post']):
            raise serializers.ValidationError("Fraudulent activity detected, rating denied.")

        return attrs

    class Meta:
        model = Rate
        fields = ('id', 'user', 'score')

    def create(self, validated_data):
        # Fraud detection

        rate, created = update_or_create_rate(
            user=validated_data['user'],
            post=validated_data['post'],
            score=validated_data['score']
        )


        return rate
