from django.db import models


class DailyPage(models.Model):
    page_date = models.DateField(unique=True)
    category = models.CharField(max_length=100, blank=True, default="")
    title = models.CharField(max_length=255)
    body = models.TextField()
    prayer = models.TextField(blank=True, default="")
    image_path = models.CharField(max_length=255, blank=True, default="")
    readings_text = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        ordering = ["page_date"]

    def __str__(self):
        return f"{self.page_date} - {self.title}"


class ReadingLink(models.Model):
    page = models.ForeignKey(
        DailyPage,
        related_name="reading_links",
        on_delete=models.CASCADE,
    )
    display_order = models.PositiveIntegerField(default=1)
    text = models.CharField(max_length=255)
    url = models.URLField(max_length=500)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.page.page_date} - {self.text}"
