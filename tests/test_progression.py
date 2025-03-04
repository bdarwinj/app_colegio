# tests/test_progression.py
import unittest
from src.utils.progression import get_next_course

class TestProgression(unittest.TestCase):
    def test_get_next_course(self):
        mapping = {
            "pre-jardin": "jardin",
            "jardin": "transicion",
            "transicion": "primero",
            "primero": "segundo",
            "segundo": "tercero",
            "tercero": "cuarto",
            "cuarto": "quinto",
            "quinto": "sexto",
            "sexto": "septimo",
            "septimo": "octavo",
            "octavo": "noveno",
            "noveno": "decimo",
            "decimo": "once",
            "once": "once"
        }
        for current, expected in mapping.items():
            self.assertEqual(get_next_course(current), expected)
            self.assertEqual(get_next_course(current.upper()), expected)

if __name__ == '__main__':
    unittest.main()
