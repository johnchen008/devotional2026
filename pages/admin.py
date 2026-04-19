from django.contrib import admin
from .models import DailyPage, ReadingLink

class ReadingLinkInline(admin.TabularInline):
    model = ReadingLink
    extra = 0


@admin.register(DailyPage)
class DailyPageAdmin(admin.ModelAdmin):
    list_display = ("title", "category")
    ordering = ("page_date",)
    search_fields = ("title", "body", "prayer", "category", "readings_text")
    list_filter = ("category",)
    inlines = [ReadingLinkInline]


@admin.register(ReadingLink)
class ReadingLinkAdmin(admin.ModelAdmin):
    list_display = ("page", "display_order", "text", "url")
    ordering = ("page", "display_order")