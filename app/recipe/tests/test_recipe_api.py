from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Ingredient
from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def recipe_url(recipe_id):
    """
    URL for a recipe
    """
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_recipe(name='Pizza', description='Put it in the oven'):
    """
    Create a sample recipe
    """
    return Recipe.objects.create(name=name, description=description)


def sample_ingredient(recipe, name='cheese'):
    """
    Create a sample ingredient
    """
    return Ingredient.objects.create(recipe=recipe, name=name)


class RecipeApiTests(TestCase):
    """
    Test Recipe API endpoints
    """

    def setUp(self):
        self.client = APIClient()

    def test_get_all_recipes(self):
        """
        GET /recipes/
        """
        recipe1 = sample_recipe()
        recipe1.ingredients.add(sample_ingredient(
            recipe=recipe1, name='dough'))
        recipe1.ingredients.add(sample_ingredient(
            recipe=recipe1, name='cheese'))

        recipe2 = sample_recipe(
            name='Beans on toast',
            description='Baked beans on white toast',
        )
        recipe2.ingredients.add(sample_ingredient(
            recipe=recipe2, name='Baked beans'))

        all_recipes = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(all_recipes, many=True)

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_get_all_recipes_using_name_filter(self):
        """
        GET /recipes/?name=<filter_term>

        with results
        """
        sample_recipe()
        recipe = sample_recipe(
            name='Beans on toast',
            description='Baked beans on white toast',
        )

        serializer = RecipeSerializer(recipe)

        filter_term = 'beans'
        res = self.client.get(
            RECIPES_URL,
            {'name': filter_term}
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data)

    def test_get_all_recipes_using_name_filter_no_results(self):
        """
        GET /recipes/?name=<filter_term>

        with no results
        """
        recipe = sample_recipe(
            name='Beans on toast',
            description='Baked beans on white toast',
        )

        filter_term = 'Pizza'
        res = self.client.get(
            RECIPES_URL,
            {'name': filter_term}
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

    def test_get_recipe_by_id_success(self):
        """
        GET /recipes/<id>/

        success
        """
        recipe = sample_recipe(
            name='Beans on toast',
            description='Baked beans on white toast',
        )
        recipe.ingredients.add(sample_ingredient(
            recipe=recipe, name='Baked beans'))

        serializer = RecipeSerializer(recipe)

        url = recipe_url(recipe.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_by_id_not_found(self):
        """
        GET /recipes/<id>/

        not found
        """
        res = self.client.get(recipe_url(recipe_id=1))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_recipe(self):
        """
        POST /recipes/

        success
        """
        payload = {
            'name': 'Pizza',
            'description': 'Put it in the oven',
            'ingredients': [{'name': 'dough'}, {'name': 'cheese'}, {'name': 'tomato'}]
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 3)

    def test_create_recipe_invalid_payload(self):
        """
        POST /recipes/

        invalid payload
        """
        payload = {
            'name': '',
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_recipe(self):
        """
        PATCH /recipes/<id>/

        success
        """
        recipe = sample_recipe()

        ingredient1 = sample_ingredient(recipe, name='dough')
        ingredient2 = sample_ingredient(recipe, name='cheese')

        recipe.ingredients.add(ingredient1, ingredient2)

        ingredients = recipe.ingredients.all()

        new_ingredient = 'tomato'
        payload = {
            'name': recipe.name,
            'description': recipe.description,
            'ingredients': [
                {'name': new_ingredient}
            ]
        }

        res = self.client.patch(recipe_url(recipe_id=recipe.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 1)
        self.assertEqual(new_ingredient, ingredients[0].name)

    def test_delete_recipe(self):
        """
        DELETE /recipes/<id>/

        success
        """
        recipe = sample_recipe()

        res = self.client.delete(recipe_url(recipe_id=recipe.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        all_recipes = Recipe.objects.all()
        self.assertEqual(len(all_recipes), 0)

        all_ingredients = Ingredient.objects.all()
        self.assertEqual(len(all_ingredients), 0)

    def test_delete_non_existing_recipe(self):
        """
        DELETE /recipes/<id>/

        doesn't exist
        """
        res = self.client.delete(recipe_url(recipe_id=1))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
