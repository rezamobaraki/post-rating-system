from django.contrib import admin

from .models.post import Post
from .models.rate import Rate


class RateInline(admin.TabularInline):
    model = Rate
    extra = 2


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'rate_count', 'average_rates')
    search_fields = ('title',)
    readonly_fields = ('rate_count', 'average_rates')
    inlines = [RateInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return []

    def average_rates(self, obj):
        from .services.queries import rates_average
        return rates_average(post=obj)

    def rate_count(self, obj):
        from .services.queries import rates_count
        return rates_count(post=obj)

    rate_count.short_description = 'Rates Count'
    average_rates.short_description = 'Average Rates'


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'score')
    search_fields = ('post__title', 'user__username', 'score')
    list_filter = ('score', 'post', 'user')
