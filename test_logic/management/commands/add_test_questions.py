import json
import uuid
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from test_logic.models import Product, Test, Question, Option  # Update 'myapp' to your actual app name


class Command(BaseCommand):
    help = "Add Test, Questions, and Options from a JSON file for a specified Product ID"

    def add_arguments(self, parser):
        parser.add_argument(
            'product_id',
            type=str,
            help='Product ID for which to add tests, questions, and options'
        )
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the JSON file containing questions and options'
        )

    def handle(self, *args, **kwargs):
        product_id = kwargs['product_id']
        file_path = kwargs['file_path']

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Product with ID {product_id} does not exist."))
            return

        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for item in data:
            # Create a new Test
            test = Test.objects.create(
                title=item.get('subject_title', 'Unnamed Test'),
                product=product,
                number_of_questions=0,  # Update later
                time=item.get('time', 45),
                score=item.get('score', 0),
                grade=item.get('class', 0),
                is_required=False
            )

            questions_count = 0

            # Add Questions and Options
            for question_data in item.get('questions', [item]):
                question = Question.objects.create(
                    test=test,
                    text=question_data.get('question', 'No Question Text'),
                    task_type=question_data.get('task_type'),
                    level=question_data.get('level'),
                    status=question_data.get('status'),
                    category=question_data.get('category'),
                    subcategory=question_data.get('subcategory'),
                    theme=question_data.get('theme'),
                    subtheme=question_data.get('subtheme'),
                    target=question_data.get('target'),
                    source=question_data.get('source'),
                    detail_id=question_data.get('detail_id'),
                    lng_id=question_data.get('lng_id'),
                    lng_title=question_data.get('lng_title'),
                    subject_id=question_data.get('subject_id'),
                    subject_title=question_data.get('subject_title'),
                    class_number=question_data.get('class', 0)
                )

                questions_count += 1

                # Add Options
                for index in range(1, 13):
                    option_text = question_data.get(f'var{index}')
                    if option_text:
                        is_correct = option_text in question_data.get('answers', [])
                        Option.objects.create(
                            question=question,
                            text=option_text,
                            is_correct=is_correct
                        )

            # Update the number of questions in the test
            test.number_of_questions = questions_count
            test.save()

        self.stdout.write(self.style.SUCCESS("Test, Questions, and Options added successfully!"))
