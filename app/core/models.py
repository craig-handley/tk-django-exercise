from django.db import models


class Recipe(models.Model):
    """
    Recipe model
    """
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Ingredient model
    """
    name = models.CharField(max_length=255)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )

    def __str__(self):
        return self.name
