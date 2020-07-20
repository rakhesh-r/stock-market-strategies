from .context import strategies
import unittest


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    @classmethod
    def setUpClass(cls) -> None:
        """setup"""
        print(__name__)
        cls._ulta_pulta = strategies.UltaPulta()

    def test_ultapulta_run(self):
        self._ulta_pulta.run()
        assert True


if __name__ == '__main__':
    unittest.main()

if __name__ == "__main__":
    print("Executed when invoked directly")
else:
    print("Executed when imported")
