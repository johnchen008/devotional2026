import csv
import json
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from pages.models import DailyPage, ReadingLink


class Command(BaseCommand):
    help = "Import devotion pages and reading links from CSV."

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)
        parser.add_argument("--overwrite", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        overwrite = options["overwrite"]

        try:
            with open(csv_file, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    page_date = datetime.strptime(row["page_date"], "%Y-%m-%d").date()

                    page, created = DailyPage.objects.get_or_create(
                        page_date=page_date,
                        defaults={
                            "category": row.get("category", ""),
                            "title": row.get("title", ""),
                            "body": row.get("body", ""),
                            "prayer": row.get("prayer", ""),
                            "image_path": row.get("image_path", ""),
                            "readings_text": row.get("readings_text", ""),
                        },
                    )

                    if created or overwrite:
                        page.category = row.get("category", "")
                        page.title = row.get("title", "")
                        page.body = row.get("body", "")
                        page.prayer = row.get("prayer", "")
                        page.image_path = row.get("image_path", "")
                        page.readings_text = row.get("readings_text", "")
                        page.save()

                        page.reading_links.all().delete()
                        links = json.loads(row.get("reading_links_json", "[]") or "[]")
                        for idx, link in enumerate(links, start=1):
                            ReadingLink.objects.create(
                                page=page,
                                display_order=idx,
                                text=link.get("text", ""),
                                url=link.get("url", ""),
                            )

            self.stdout.write(self.style.SUCCESS("Import completed successfully."))
        except FileNotFoundError:
            raise CommandError(f"CSV file not found: {csv_file}")
        except Exception as exc:
            raise CommandError(str(exc))
