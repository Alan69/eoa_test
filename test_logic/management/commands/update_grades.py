from django.core.management.base import BaseCommand
from test_logic.models import Test, Product  # Adjust the import path as needed

class Command(BaseCommand):
    help = 'Update grades by increasing each grade by 3 for a specific product ID'

    def handle(self, *args, **kwargs):
        product_id = '59c6f3a4-14e9-4270-a859-c1131724f51c'

        # Filter tests for the specific product with grades between 1 and 8
        tests_to_update = Test.objects.filter(product__id=product_id, grade__in=range(1, 9))

        if not tests_to_update.exists():
            self.stdout.write(f"No tests found for product ID {product_id} with grades between 1 and 8.")
            return

        # Update each grade
        for test in tests_to_update:
            old_grade = test.grade
            test.grade += 3
            test.save()
            self.stdout.write(f"Updated Test ID {test.id}: {old_grade} -> {test.grade}")

        self.stdout.write(f"Successfully updated {tests_to_update.count()} test grades for product {product_id}.")
