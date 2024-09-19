from rest_framework import serializers

from posts.enums import RateScoreEnum
from posts.models import Rate
from posts.services.commands import update_or_create_rate
from posts.services.queries import update_post_cache


class RateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    score = serializers.IntegerField(
        required=True, min_value=RateScoreEnum.ZERO_STARS, max_value=RateScoreEnum.FIVE_STARS
    )

    class Meta:
        model = Rate
        fields = ('id', 'user', 'score')

    def create(self, validated_data):
        rate, created = update_or_create_rate(
            user=validated_data['user'],
            post=validated_data['post'],
            score=validated_data['score']
        )
        update_post_cache(validated_data['post'])
        return rate
