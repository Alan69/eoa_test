import uuid
from django.core.management.base import BaseCommand
from test_logic.models import Question  # Replace `myapp` with your app's name


class Command(BaseCommand):
    help = 'Counts Question objects where text is None or an empty string'

    def handle(self, *args, **options):
        # Query for questions where text is None or empty
        empty_text_count = Question.objects.filter(text__isnull=True).count() + \
                           Question.objects.filter(text="").count()
        
        # Output the count
        self.stdout.write(self.style.SUCCESS(f'Number of Questions with empty or null text: {empty_text_count}'))
