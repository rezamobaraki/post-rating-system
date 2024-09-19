from rest_framework import serializers

from posts.models.post import Post
from posts.services.queries import rates_average, rates_count


class PostSerializer(serializers.ModelSerializer):
    average_rates = serializers.SerializerMethodField()
    total_rates = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'average_rates', 'total_rates')

    def get_average_rates(self, obj):
        return rates_average(post=obj)

    def get_total_rates(self, obj):
        return rates_count(post=obj)
