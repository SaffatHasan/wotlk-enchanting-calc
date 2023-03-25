from nexushub_api import Reagent
import unittest

class ReagentTest(unittest.TestCase):

    def test_dict(self):
        # https://wotlk.professions.gg/profession/enchanting
        r = Reagent(
            id=7421,
            name="foo",
            price=1234,
        )
        self.assertEqual(r.__dict__(), {"id": 7421, "name": "foo", "price": 1234})

if __name__ == "__main__":
    unittest.main()
