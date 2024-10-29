from django.core.management.base import BaseCommand
from test_logic.models import Test  # Adjust import if needed

class Command(BaseCommand):
    help = 'Set grade to 0 for tests with None grade'

    def handle(self, *args, **kwargs):
        # Filter tests where grade is None
        tests_to_update = Test.objects.filter(grade__isnull=True)

        if not tests_to_update.exists():
            self.stdout.write("No tests found with grade = None.")
            return

        # Update each test with grade = None to grade = 0
        for test in tests_to_update:
            test.grade = 0
            test.save()
            self.stdout.write(f"Updated Test ID {test.id}: grade = None -> 0")

        self.stdout.write(f"Successfully updated {tests_to_update.count()} tests.")
