from django.contrib import admin

from .models.post import Post
from .models.rate import Rate


class RateInline(admin.TabularInline):
    model = Rate
    fields = ('user', 'score')
    extra = 2


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'total_rates', 'average_rates')
    search_fields = ('title',)
    readonly_fields = ('total_rates', 'average_rates')
    inlines = [RateInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return []

    def average_rates(self, obj):
        from .services.queries import get_post_stats
        return get_post_stats(post_id=obj.id)['average_rate']

    def total_rates(self, obj):
        from .services.queries import get_post_stats
        return get_post_stats(post_id=obj.id)['total_rates']

    total_rates.short_description = 'Total Rates'
    average_rates.short_description = 'Average Rates'


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'score')
    search_fields = ('post__title', 'user__username', 'score')
    list_filter = ('score', 'post', 'user')
