from rest_framework import serializers

from posts.enums import RateScoreEnum
from posts.models import Rate


class RateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    score = serializers.IntegerField(
        required=True, min_value=RateScoreEnum.ZERO_STARS, max_value=RateScoreEnum.FIVE_STARS
    )

    class Meta:
        model = Rate
        fields = ('id', 'user', 'score')

    def create(self, validated_data):
        rating, created = Rate.objects.update_or_create(
            user=validated_data['user'],
            post=validated_data['post'],
            defaults={'score': validated_data['score']}
        )
        return rating
