from django.core.management.base import BaseCommand
from test_logic.models import Test

class Command(BaseCommand):
    help = 'Update grades by increasing each grade by 3'

    def handle(self, *args, **kwargs):
        # Filter tests with grades between 1 and 8
        tests_to_update = Test.objects.filter(grade__in=range(1, 9))

        # Update each grade
        for test in tests_to_update:
            old_grade = test.grade
            test.grade += 3
            test.save()
            self.stdout.write(f"Updated Test ID {test.id}: {old_grade} -> {test.grade}")

        self.stdout.write(f"Successfully updated {tests_to_update.count()} test grades.")
