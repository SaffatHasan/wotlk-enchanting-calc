from recipes import Recipe
import unittest

class RecipeTest(unittest.TestCase):

    def test_expected_times_per_skillup(self):
        # https://wotlk.professions.gg/profession/enchanting?level=1&range=1,2&recipe=runed-copper-rod&type=guide
        someRecipe = Recipe(
            id=7421,
            name="runed copper rod",
            reagents={},
            colors=[
                1, 5, 7, 10
            ],
        )

        # 100% chance to level up when orange 
        self.assertEqual(someRecipe.levelup_probability(1), 1)
        self.assertEqual(someRecipe.expected_times_per_skillup(1), 1)

        # 80% chance at level 6
        self.assertEqual(someRecipe.levelup_probability(6), 0.8)
        # 1.25 average attempts is rounded down to 1
        self.assertEqual(someRecipe.expected_times_per_skillup(6), 1)

        # 40% chance at level 8
        self.assertEqual(someRecipe.levelup_probability(8), 0.4)
        # 2.5 average attempts is rounded down to 2
        self.assertEqual(someRecipe.expected_times_per_skillup(8), 2)




if __name__ == "__main__":
    unittest.main()
