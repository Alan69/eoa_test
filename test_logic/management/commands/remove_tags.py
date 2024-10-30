import re
from django.core.management.base import BaseCommand
from test_logic.models import Question, Option  # Adjust import path if needed

class Command(BaseCommand):
    help = 'Remove HTML tags from the text field of all Question and Option objects.'

    # Regular expression to match all HTML tags
    TAG_RE = re.compile(r'<[^>]+>')

    def handle(self, *args, **kwargs):
        # Update questions
        self.stdout.write("Processing Questions...")
        question_updates = self.remove_html_tags_from_questions()

        # Update options
        self.stdout.write("Processing Options...")
        option_updates = self.remove_html_tags_from_options()

        # Summary
        self.stdout.write(f"Successfully updated {question_updates} questions.")
        self.stdout.write(f"Successfully updated {option_updates} options.")

    def remove_html_tags_from_questions(self):
        updated_count = 0
        questions = Question.objects.all()

        for question in questions:
            original_text = question.text or ""  # Handle None as empty string
            cleaned_text = self.TAG_RE.sub('', original_text)

            if cleaned_text != original_text:
                question.text = cleaned_text
                question.save()
                updated_count += 1
                self.stdout.write(f"Updated Question ID {question.id}")

        return updated_count

    def remove_html_tags_from_options(self):
        updated_count = 0
        options = Option.objects.all()

        for option in options:
            original_text = option.text or ""  # Handle None as empty string
            cleaned_text = self.TAG_RE.sub('', original_text)

            if cleaned_text != original_text:
                option.text = cleaned_text
                option.save()
                updated_count += 1
                self.stdout.write(f"Updated Option ID {option.id}")

        return updated_count
