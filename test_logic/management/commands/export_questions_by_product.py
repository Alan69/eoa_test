from django.core.management.base import BaseCommand, CommandError
import json
import uuid
import pandas as pd
import os
from test_logic.models import Product, Test, Question, Option

class Command(BaseCommand):
    help = 'Export questions for a specific product ID to JSON or Excel files'

    def add_arguments(self, parser):
        parser.add_argument('product_id', type=str, help='UUID of the product to export questions from')
        parser.add_argument('--output', type=str, default='questions_export.json', help='Output file name')
        parser.add_argument('--test_id', type=str, default=None, help='UUID of the test to export questions from (optional)')

    def handle(self, *args, **options):
        product_id = options['product_id']
        output_file = options['output']
        test_id = options['test_id']
        
        try:
            # Validate UUID format
            uuid_obj = uuid.UUID(product_id)
            
            # Check if product exists
            try:
                product = Product.objects.get(id=uuid_obj)
            except Product.DoesNotExist:
                raise CommandError(f"Product with ID {product_id} does not exist")
            
            # Get tests for this product (all or by test_id)
            if test_id:
                try:
                    test_uuid = uuid.UUID(test_id)
                    tests = Test.objects.filter(id=test_uuid, product=product)
                except ValueError:
                    raise CommandError(f"Invalid UUID format: {test_id}")
                
                # Export single test to JSON
                self._export_to_json(tests, product, output_file, test_id)
            else:
                tests = Test.objects.filter(product=product)
                
                if not tests.exists():
                    self.stdout.write(self.style.WARNING(f"No tests found for product '{product.title}' (ID: {product_id})"))
                    return
                
                # Export each test to separate Excel files
                self._export_to_excel_files(tests, product)
            
        except ValueError:
            raise CommandError(f"Invalid UUID format: {product_id}")

    def _export_to_json(self, tests, product, output_file, test_id=None):
        """Export tests to JSON format"""
        if not tests.exists():
            self.stdout.write(self.style.WARNING(f"No tests found for product '{product.title}'"))
            return
            
        data = []
        question_count = 0
        
        for test in tests:
            questions = Question.objects.filter(test=test)
            
            for question in questions:
                options = Option.objects.filter(question=question)
                
                question_data = {
                    "model": "test_logic.question",
                    "pk": str(question.id),
                    "fields": {
                        "test": {
                            "id": str(question.test.id),
                            "title": question.test.title
                        },
                        "text": question.text,
                        "text2": question.text2,
                        "text3": question.text3,
                        "img": question.img.url if question.img and question.img.name else None,
                        "task_type": question.task_type,
                        "level": question.level,
                        "status": question.status,
                        "category": question.category,
                        "subcategory": question.subcategory,
                        "theme": question.theme,
                        "subtheme": question.subtheme,
                        "target": question.target,
                        "source": question.source,
                        "detail_id": question.detail_id,
                        "lng_id": question.lng_id,
                        "lng_title": question.lng_title,
                        "subject_id": question.subject_id,
                        "subject_title": question.subject_title,
                        "class_number": question.class_number,
                        "options": [
                            {
                                "id": str(option.id),
                                "text": option.text,
                                "is_correct": option.is_correct,
                                "img": option.img.url if option.img and option.img.name else None
                            } for option in options
                        ]
                    }
                }
                
                data.append(question_data)
                question_count += 1
        
        # Write to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully exported {question_count} questions from product "{product.title}" (ID: {product.id})' + (f' and test (ID: {test_id})' if test_id else '') + f' to {output_file}'
            )
        )

    def _export_to_excel_files(self, tests, product):
        """Export each test to a separate Excel file"""
        total_questions = 0
        files_created = 0
        
        for test in tests:
            questions = Question.objects.filter(test=test)
            
            if not questions.exists():
                continue
                
            # Prepare data for Excel
            excel_data = []
            
            for question in questions:
                options = Option.objects.filter(question=question)
                
                # Format options as a single string
                options_text = " | ".join([
                    f"{self._clean_text_for_excel(option.text)}{' (correct)' if option.is_correct else ''}"
                    for option in options
                ])
                
                excel_data.append({
                    'Question ID': str(question.id),
                    'Test ID': str(test.id),
                    'Test Title': self._clean_text_for_excel(test.title),
                    'Question Text': self._clean_text_for_excel(question.text),
                    'Question Text 2': self._clean_text_for_excel(question.text2),
                    'Question Text 3': self._clean_text_for_excel(question.text3),
                    'Task Type': question.task_type,
                    'Level': question.level,
                    'Status': question.status,
                    'Category': self._clean_text_for_excel(question.category),
                    'Subcategory': self._clean_text_for_excel(question.subcategory),
                    'Theme': self._clean_text_for_excel(question.theme),
                    'Subtheme': self._clean_text_for_excel(question.subtheme),
                    'Target': self._clean_text_for_excel(question.target),
                    'Source': self._clean_text_for_excel(question.source),
                    'Detail ID': question.detail_id,
                    'Language ID': question.lng_id,
                    'Language Title': self._clean_text_for_excel(question.lng_title),
                    'Subject ID': question.subject_id,
                    'Subject Title': self._clean_text_for_excel(question.subject_title),
                    'Class Number': question.class_number,
                    'Options': options_text,
                    'Image': question.img.url if question.img and question.img.name else None
                })
            
            # Create DataFrame
            df = pd.DataFrame(excel_data)
            
            # Create safe filename
            safe_product_title = self._make_safe_filename(product.title)
            safe_test_title = self._make_safe_filename(test.title)
            filename = f"{safe_product_title}_{safe_test_title}.xlsx"
            
            # Export to Excel
            df.to_excel(filename, index=False, engine='openpyxl')
            
            total_questions += len(excel_data)
            files_created += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {filename} with {len(excel_data)} questions'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully exported {total_questions} questions from {files_created} tests of product "{product.title}"'
            )
        )

    def _clean_text_for_excel(self, text):
        """Clean text to remove characters that are illegal in Excel worksheets"""
        if not text:
            return text
        
        # Convert to string if not already
        text = str(text)
        
        # Remove or replace illegal characters for Excel
        # Excel doesn't allow these control characters: 0x00-0x08, 0x0B, 0x0C, 0x0E-0x1F, 0x7F-0x9F
        import re
        
        # Remove control characters that cause issues in Excel
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        # Replace some problematic characters
        text = text.replace('\x0A', ' ')  # Replace newlines with spaces
        text = text.replace('\x0D', ' ')  # Replace carriage returns with spaces
        
        # Limit length to avoid Excel cell limit issues (32767 characters)
        if len(text) > 32000:
            text = text[:32000] + "..."
        
        return text

    def _make_safe_filename(self, text):
        """Convert text to safe filename by removing/replacing invalid characters"""
        if not text:
            return "untitled"
        
        # Replace invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        safe_text = text
        for char in invalid_chars:
            safe_text = safe_text.replace(char, '_')
        
        # Remove extra spaces and replace with underscores
        safe_text = '_'.join(safe_text.split())
        
        # Limit length to avoid filesystem issues
        if len(safe_text) > 50:
            safe_text = safe_text[:50]
        
        return safe_text 