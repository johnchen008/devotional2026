from datetime import date
from django.shortcuts import get_object_or_404, render
from .models import DailyPage


def home(request):
    today = date.today()
    page = DailyPage.objects.filter(page_date=today).first()
    if not page:
        page = DailyPage.objects.order_by("page_date").first()
    if not page:
        return render(request, "pages/daily_page.html", {"page": None, "reading_links": []})
    return daily_page(request, str(page.page_date))


def daily_page(request, page_date):
    page = get_object_or_404(
        DailyPage.objects.prefetch_related("reading_links"),
        page_date=page_date,
    )
    reading_links = page.reading_links.order_by("display_order")
    prev_page = DailyPage.objects.filter(page_date__lt=page.page_date).order_by("-page_date").first()
    next_page = DailyPage.objects.filter(page_date__gt=page.page_date).order_by("page_date").first()

    return render(
        request,
        "pages/daily_page.html",
        {
            "page": page,
            "reading_links": reading_links,
            "prev_page": prev_page,
            "next_page": next_page,
        },
    )
