import uuid
from django.core.management.base import BaseCommand
from test_logic.models import Question  # Replace `myapp` with your app's name


class Command(BaseCommand):
    help = 'Counts and optionally deletes Question objects where text is None or an empty string'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete questions with empty or null text',
        )

    def handle(self, *args, **options):
        # Query for questions with empty or null text
        empty_text_questions = Question.objects.filter(text__isnull=True) | Question.objects.filter(text="")
        empty_text_count = empty_text_questions.count()

        if options['delete']:
            # Delete the questions
            empty_text_questions.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {empty_text_count} Questions with empty or null text'))
        else:
            # Just count
            self.stdout.write(self.style.SUCCESS(f'Number of Questions with empty or null text: {empty_text_count}'))