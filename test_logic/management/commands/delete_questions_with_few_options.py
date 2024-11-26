import uuid
from django.core.management.base import BaseCommand
from test_logic.models import Question, Test
from django.db import models

class Command(BaseCommand):
    help = 'Delete Questions with less than 4 options for a specific Test ID'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-id',
            type=str,
            required=False,
            default='1f886430-2014-44fe-af88-1530208a597d',
            help='The ID of the Test to filter Questions',
        )

    def handle(self, *args, **options):
        test_id = options['test_id']

        # Validate the Test ID
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Test with ID {test_id} does not exist.'))
            return

        # Filter Questions by Test ID and check option count
        questions_to_delete = Question.objects.filter(test=test).annotate(option_count=models.Count('options')).filter(option_count__lt=4)
        num_deleted, _ = questions_to_delete.delete()

        # Output the result
        if num_deleted > 0:
            self.stdout.write(self.style.SUCCESS(f'Deleted {num_deleted} Questions with fewer than 4 options for Test ID {test_id}.'))
        else:
            self.stdout.write(self.style.WARNING(f'No Questions with fewer than 4 options found for Test ID {test_id}.'))
