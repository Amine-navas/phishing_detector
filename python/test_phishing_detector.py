import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from phishing_detector import PhishingEngine


class PhishingEngineTests(unittest.TestCase):
    def test_fit_and_predict_on_small_dataset(self):
        engine = PhishingEngine()
        texts = [
            "Free money now",
            "Meeting tomorrow",
            "Claim your prize",
            "Let's discuss project",
        ]
        labels = [1, 0, 1, 0]

        engine.fit(texts, labels)
        label, confidence = engine.predict("You won a free prize")

        self.assertIn(label, (0, 1))
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)


if __name__ == "__main__":
    unittest.main()
