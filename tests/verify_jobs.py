
import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_manager import DataManager

class MockGame:
    def __init__(self):
        pass

class TestJobSystem(unittest.TestCase):
    def setUp(self):
        self.game = MockGame()
        self.data_manager = DataManager(self.game)
        self.data_manager.load_data()

    def test_jobs_loaded(self):
        jobs = self.data_manager.data['jobs']
        self.assertIn('warrior', jobs)
        self.assertIn('mage', jobs)
        
    def test_warrior_stats(self):
        warrior = self.data_manager.data['jobs']['warrior']
        self.assertEqual(warrior['base_stats']['strength'], 10)
        self.assertEqual(warrior['next_tier'], 'gladiator')

    def test_skills_loaded(self):
        mage = self.data_manager.data['jobs']['mage']
        self.assertTrue(len(mage['skills']) > 0)
        self.assertEqual(mage['skills'][0]['name'], 'Frizz Mastery')

if __name__ == '__main__':
    unittest.main()
