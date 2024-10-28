import json
import os
import uuid
from test_logic.models import Test, Question, Option, Product
from django.core.management.base import BaseCommand  # Required for custom management commands

class Command(BaseCommand):
    help = 'Import quiz data from JSON file'

    def handle(self, *args, **kwargs):
        # Construct the file path dynamically
        file_path = os.path.join(os.path.dirname(__file__), 'quiz_data.json')

        # Ensure the specified Product exists
        product_id = uuid.UUID("4ce7261c-29e8-4514-94c0-68344010c2d9")
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Product with ID {product_id} does not exist."))
            return

        # Open and load the JSON file
        with open(file_path, 'r', encoding='utf-8') as file:
            quizzes = json.load(file)

        for quiz_data in quizzes:
            # Process only quizzes with lng_title "казахский"
            if quiz_data['lng_title'] != "казахский":
                continue

            # Create a new Test entry
            test = Test.objects.create(
                title=quiz_data['subject_title'],
                grade=quiz_data['grade'],
                product=product  # Set the specified product
            )

            # Iterate over questions for this quiz
            for question_data in quiz_data['questions']:
                # Create a new Question entry
                question = Question.objects.create(
                    test=test,
                    text=question_data['question'],
                    img=question_data['image_path'] if question_data['image_path'] else None
                )

                # Create Option entries
                options = [
                    {"text": question_data['var1'], "is_correct": question_data['answers'] == question_data['var1']},
                    {"text": question_data['var2'], "is_correct": question_data['answers'] == question_data['var2']},
                    {"text": question_data['var3'], "is_correct": question_data['answers'] == question_data['var3']},
                    {"text": question_data['var4'], "is_correct": question_data['answers'] == question_data['var4']},
                    {"text": question_data['var5'], "is_correct": question_data['answers'] == question_data['var5']}
                ]

                # Create and link options to the question
                for option_data in options:
                    Option.objects.create(
                        question=question,
                        text=option_data['text'],
                        is_correct=option_data['is_correct']
                    )

        self.stdout.write(self.style.SUCCESS("Data import completed successfully."))
