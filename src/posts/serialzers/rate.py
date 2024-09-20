from rest_framework import serializers

from commons.fraud_detection import FraudDetection
from posts.enums import RateScoreEnum
from posts.models import Rate
from posts.services.commands import update_or_create_rate


class RateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    score = serializers.IntegerField(
        required=True, min_value=RateScoreEnum.ZERO_STARS, max_value=RateScoreEnum.FIVE_STARS
    )
    is_suspected = serializers.HiddenField(default=False)

    def validate(self, data):
        if FraudDetection.is_fraudulent_action(user_id=data['user'].id, post_id=data['post'].id):
            data['is_suspected'] = True
        return data

    class Meta:
        model = Rate
        fields = ('id', 'user', 'score')

    def create(self, validated_data):
        rate, created = update_or_create_rate(
            user_id=validated_data['user'].id,
            post_id=validated_data['post'].id,
            score=validated_data['score'],
            is_suspected=validated_data['is_suspected']
        )

        return rate
