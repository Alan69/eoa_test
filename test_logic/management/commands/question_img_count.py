import re
from django.core.management.base import BaseCommand
from test_logic.models import Question  # Adjust the import path if needed

class Command(BaseCommand):
    help = 'Delete questions that contain <img> tags in the text field.'

    def handle(self, *args, **kwargs):
        # Regex pattern to match <img> tags
        img_tag_pattern = re.compile(r'<img\s+[^>]*>', re.IGNORECASE)

        # Get all Question objects
        questions = Question.objects.all()

        # Track how many questions are deleted
        deleted_count = 0

        # Iterate over questions and delete those with <img> tags
        for question in questions:
            text = question.text or ""  # Handle None text as empty string

            # Check if the text contains any <img> tags
            if img_tag_pattern.search(text):
                self.stdout.write(f"Deleting Question ID {question.id} with <img> tag.")
                question.delete()
                deleted_count += 1

        # Final output with the number of deleted questions
        self.stdout.write(f"Deleted {deleted_count} questions containing <img> tags.")
