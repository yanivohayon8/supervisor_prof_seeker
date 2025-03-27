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


    def test_extract_abstract_1(self):
        text = """
            Vision Research 228 (2025) 108546
            Available online 31 January 2025
            0042-6989/© 2025 The Authors. Published by Elsevier Ltd. This is an open access article under the CC BY-NC-ND license (http://creativecommons.org/licenses/by-
            nc-nd/4.0/).
            Contents lists available at ScienceDirect
            Vision Research
            journal homepage: www.elsevier.com/locate/visres
            The Polar Saccadic Flow model: Re-modeling the center bias from fixations to
            saccades
            Rotem Mairon, Ohad Ben-Shahar ∗
            Department of Computer Science, Ben-Gurion University of the Negev, Israel
            School of Brain Sciences and Cognition, Ben-Gurion University of the Negev, Israel
            A R T I C L E
            I N F O
            Keywords:
            Eye-movements
            Saccades
            Center bias
            Polar representation
            Mixture models
            A B S T R A C T
            Research indicates that a significant component of human eye movement behavior constitutes a set of consistent
            biases independent of visual content, the most well-known of which is the central bias. While all prior art
            focuses on representing saccadic motion and biases in Cartesian retinotopic coordinates, here we propose
            the Polar Saccadic Flow model, a novel approach for modeling saccades’ space-dependent biases in a polar
            representation. By breaking saccades into orientation and amplitude, the Polar Saccadic Flow model enables
            more accurate modeling of these components, leading also to a better understanding of the saccadic bias.
            Moreover, the polar representation also uncovers hitherto unknown patterns and biases in eye movement data,
            allowing for a more detailed and nuanced analysis of saccadic behavior. These findings have implications for
            the study of human visual perception, can help to develop more accurate eye movement models, and also may
            improve eye tracking technologies.
            1. Introduction and background
            The center bias is a prevalent tendency in human eye movement
            behavior. Regardless of various factors that influence eye movements,
            such as task demands, the visual stimuli itself, and individual differ-
            ences, observers consistently exhibit a strong inclination to direct their
            gaze centrally. Understanding this persistent center bias is crucial as it
            can shed light on the underlying mechanisms driving visual attention
            and perception.
        """

        abstract = pdf_handler.extract_absract(text)


        self.assertIsNotNone(abstract)
        self.assertIsNot(len(abstract),0)
        self.assertNotIn("Introduction",abstract)
        assert abstract.endswith("1. ")

    def test_extract_abstract_2(self):
        text = """Recognizing Artistic Style of Archaeological
        Image Fragments Using Deep Style Extrapolation
        Gur Elkin , Ofir Itzhak Shahar , Yaniv Ohayon , Nadav Alali , and Ohad
        Ben-Shahar
        Ben-Gurion University of the Negev
        {gurshal, shofir, yanivoha, nadavala}@post.bgu.ac.il, obs@bgu.ac.il
        Abstract. Ancient artworks obtained in archaeological excavations usu-
        ally suffer from a certain degree of fragmentation and physical degrada-
        tion. Often, fragments of multiple artifacts from different periods or artis-
        tic styles could be found on the same site. With each fragment containing
        only partial information about its source, and pieces from different ob-
        jects being mixed, categorizing broken artifacts based on their visual
        cues could be a challenging task, even for professionals. As classification
        is a common function of many machine learning models, the power of
        modern architectures can be harnessed for efficient and accurate frag-
        ment classification. In this work, we present a generalized deep-learning
        framework for predicting the artistic style of image fragments, achieving
        state-of-the-art results for pieces with varying styles and geometries.
        Keywords: Image Classification · Artistic Style · Cultural Heritage.
        1
        Introduction
        The ability to automatically recognize and classify artistic styles from images
        """

        abstract = pdf_handler.extract_absract(text)

        self.assertIsNotNone(abstract)
        self.assertIsNot(len(abstract),0)
        self.assertNotIn("Introduction",abstract)

    def test_extract_introduction_1(self):
        text = """
        results against strong baselines. In the unconditional generation tasks, we show
        remarkable mean improvements of 58.17% over previous diffusion models in the
        short discriminative score and 132.61% in the (ultra-)long classification scores.
        Code is at https://github.com/azencot-group/ImagenTime.
        1
        Introduction
        Generative modeling of real-world information such as images [72], texts [13], and other types of
        data [99, 55, 8] has drawn increased attention recently. In this work, we focus on the setting of
        1. We view generative modeling of time series as a visual challenge, allowing to harness advances in
        time series to image transforms as well as vision diffusion models.
        2. We develop a novel generative model for time series that scales from short to very long sequence
        lengths without significant modifications to the neural architecture or training method.
        3. Our approach achieves state-of-the-art results in comparison to strong baselines in unconditional
        and conditional generative benchmarks for time series of lengths in the range [24, 17.5k]. Particularly,
        we attain the best scores on a new challenging benchmark of very long sequences that we introduce.
        2
        Related work
        Time series to image works.
        Motivated by the success of c
        """

        intro = pdf_handler.extract_introduction(text)
        self.assertIsNotNone(intro)
        self.assertIsNot(len(intro),0)
        assert intro.endswith("Related work")

    def test_read_abstract_intro_1(self):
        in_path = "tests/data/Harel_et_al-2024-International_Journal_of_Computer_Vision.pdf"
        text = pdf_handler.read_pdf(in_path)
        abstract = pdf_handler.extract_absract(text)
        self.assertNotEqual(len(abstract),0)
        intro = pdf_handler.extract_introduction(text)
        self.assertNotEqual(len(intro),0)

if __name__ == "__main__":
    unittest.main()