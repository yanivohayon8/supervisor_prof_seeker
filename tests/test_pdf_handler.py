import unittest
from src import pdf_handler

class TestCleaning(unittest.TestCase):

    def test_clean_1(self):
        text = '''The ability to automatically recognize and classify artistic styles from images
                is a challenging problem in computer vision and digital art analysis. Artistic
                styles encompass the distinctive visual patterns, techniques, and movements
                that characterize the works of different artists, periods, and schools through-
                out history [35]. Accurately identifying these styles holds significant value for
                applications such as archiving and cataloging art collections, supporting art ed-
                ucation and appreciation [34], and enabling content-based image retrieval and
                recommendation systems [7].'''
        
        text = pdf_handler.clean_(text)

        self.assertNotIn("\n",text)
        self.assertNotIn("[7]",text)
        self.assertNotIn("[34]",text)


if __name__ == "__main__":
    unittest.main()