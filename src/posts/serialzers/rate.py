from rest_framework import serializers

from commons.fraud_detection import FraudDetection
from posts.enums import RateScoreEnum
from posts.models import Rate
from posts.services.commands.rate import update_or_create_rate


class RateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    score = serializers.IntegerField(
        required=True, min_value=RateScoreEnum.ZERO_STARS, max_value=RateScoreEnum.FIVE_STARS
    )
    is_suspected = serializers.HiddenField(default=False, write_only=True)

    class Meta:
        model = Rate
        fields = ('id', 'user', 'score', 'is_suspected')

    def create(self, validated_data):
        if FraudDetection.is_fraudulent_action(post_id=validated_data['post'].id):
            validated_data['is_suspected'] = True

        update_or_create_rate(
            user_id=validated_data['user'].id,
            post_id=validated_data['post'].id,
            score=validated_data['score'],
            is_suspected=validated_data['is_suspected']
        )

        return {
            'user': validated_data['user'],
            'post': validated_data['post'],
            'score': validated_data['score'],
        }
