from rest_framework import serializers

from posts.models.post import Post
from posts.services.queries import get_post_stats


class PostSerializer(serializers.ModelSerializer):
    average_rates = serializers.SerializerMethodField()
    total_rates = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'average_rates', 'total_rates')

    def get_average_rates(self, obj):
        return get_post_stats(post_id=obj.id).get('average_rates')

    def get_total_rates(self, obj):
        return get_post_stats(post_id=obj.id).get('total_rates')
