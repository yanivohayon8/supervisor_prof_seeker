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

    
    def test_read_pdf_internal_func(self):
        in_path = "tests/data/Harel_et_al-2024-International_Journal_of_Computer_Vision.pdf"
        text = pdf_handler.read_pdf_text_(in_path)
        print(text)
        self.assertNotEqual(len(text),0)
    
    def test_remove_references(self):
        text = """This research was partially supported by
                References
                [1] J. Allen. Short term spectral analysis, synthesis, and modification by discrete Fourier transform. IEEE
                transactions on acoustics, speech, and signal processing, 25(3):235–238, 1977.
                [2] J. B. Allen and L. R. Rabiner. A unified approach to short-time Fourier analysis and synthesis. Proceedings
                of the IEEE, 65(11):1558–1564, 1977.
                [3] S.-I. Amari. Learning patterns and pattern sequences by self-organizing nets of threshold elements. IEEE
                Transactions on computers, 100(11):1197–1206, 1972.
                [4] B. D. Anderson. Reverse-time diffusion equation models. Stochastic Processes and their Applications,
                12(3):313–326, 1982.
                [5] M. Arjovsky, A. Shah, and Y. Bengio. Unitary evolution recurrent neural networks. In International
                conference on machine learning. PMLR, 2016.
                [6] O. Azencot, N. B. Erichson, V. Lin, and M. Mahoney. Forecasting sequential data using consistent
                Koopman autoencoders. In International Conference on Machine Learning, pages 475–485. PMLR,
                2020.
                
                Apenndix
                yada yada
                """

        text = pdf_handler.remove_references_(text)
        # print(text)

        self.assertEqual(text,"""This research was partially supported by
                """)

    def test_read_pdf(self):
        in_path = "tests/data/Harel_et_al-2024-International_Journal_of_Computer_Vision.pdf"
        text = pdf_handler.read_pdf(in_path)
        # print(text)
        self.assertNotEqual(len(text),0)




if __name__ == "__main__":
    unittest.main()