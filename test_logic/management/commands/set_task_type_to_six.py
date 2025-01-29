from django.core.management.base import BaseCommand
from test_logic.models import Question  # Replace app_name with your app name

class Command(BaseCommand):
    help = "Set task_type to 10 for questions with exactly 8 options"

    def handle(self, *args, **kwargs):
        questions = Question.objects.all()
        updated_count = 0

        for question in questions:
            if question.options.count() == 6:  # Check related options count
                question.task_type = 6
                question.save()
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Updated task_type for {updated_count} questions.")
        )
