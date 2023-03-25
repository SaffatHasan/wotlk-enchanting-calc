from nexushub_api import NexusHubApi
from profession import Engineering
import unittest

class EngineeringTest(unittest.TestCase):

    def test_load(self):
        engi = Engineering(nexus_hub_api=NexusHubApi("sulfuras", "horde"))
        self.assertGreater(len(engi.recipes), 0)


if __name__ == "__main__":
    unittest.main()
