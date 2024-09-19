from rest_framework import serializers

from posts.models.post import Post


class PostSerializer(serializers.ModelSerializer):
    average_rates = serializers.SerializerMethodField()
    total_rates = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'average_rates', 'total_rates')
