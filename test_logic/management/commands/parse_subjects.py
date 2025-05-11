import json
import os
from django.core.management.base import BaseCommand
from test_logic.models import Question
from django.conf import settings

class Command(BaseCommand):
    help = 'Parse subjects JSON files and create Question objects'

    def handle(self, *args, **options):
        # Use BASE_DIR to construct the absolute path
        subjects_dir = os.path.join(settings.BASE_DIR, 'subjects')
        if not os.path.exists(subjects_dir):
            self.stdout.write(self.style.ERROR(f'Subjects directory does not exist: {subjects_dir}'))
            return
        
        for filename in os.listdir(subjects_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(subjects_dir, filename)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    subject_id = data.get('subject_id')
                    questions = data.get('questions', [])
                    
                    for question_data in questions:
                        # Get base fields
                        question_text = question_data.get('question', '')
                        options = question_data.get('options', [])
                        group_text = question_data.get('group_text', '')
                        original_task_type = question_data.get('task_type')
                        
                        # Determine task type based on conditions
                        if group_text:
                            task_type = 10
                        elif original_task_type == 5:
                            task_type = 6
                        elif original_task_type == 14:
                            task_type = 8
                            # Handle special case for task_type 14
                            if len(options) >= 6:
                                text2 = options[0]
                                text3 = options[1]
                                # Multiply options 3-6 by 2
                                multiplied_options = []
                                for i in range(2, 6):
                                    if i < len(options):
                                        multiplied_options.extend([options[i], options[i]])
                                options = [text2, text3] + multiplied_options
                        else:
                            task_type = original_task_type
                        
                        # Create Question object
                        Question.objects.create(
                            test=subject_id,
                            text=question_text,
                            options=options,
                            task_type=task_type
                        )
                        
                self.stdout.write(self.style.SUCCESS(f'Successfully parsed {filename}')) 