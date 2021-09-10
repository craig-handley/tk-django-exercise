from django.test import TestCase
from core import models


class ModelTests(TestCase):

    def test_ingredient_str(self):
        """
        Test the Ingredient string representation
        """
        recipe = models.Recipe.objects.create(
            name='Pizza',
            description='Put it in the oven',
        )

        ingredient = models.Ingredient.objects.create(
            recipe=recipe,
            name='cheese'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """
        Test the Recipe string representation
        """
        recipe = models.Recipe.objects.create(
            name='Pizza',
            description='Put it in the oven',
        )

        self.assertEqual(str(recipe), recipe.name)
