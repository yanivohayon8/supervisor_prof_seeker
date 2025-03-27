import unittest
from src import pdf_handler

class TestCleaning(unittest.TestCase):

    def test_clean_1(self):
        text = '''Transformer models have consistently achieved remarkable results in various domains such
                as natural language processing and computer vision. However, despite ongoing research
                efforts to better understand these models, the field still lacks a comprehensive understand-
                ing. This is particularly true for deep time series forecasting methods, where analysis and
                understanding work is relatively limited. Time series data, unlike image and text informa-
                tion, can be more challenging to interpret and analyze. To address this, we approach the
                problem from a manifold learning perspective, assuming that the latent representations of
                time series forecasting models lie next to a low-dimensional manifold. In our study, we focus
                on analyzing the geometric features of these latent data manifolds, including intrinsic di-
                mension and principal curvatures. Our findings reveal that deep transformer models exhibit
                similar geometric behavior across layers, and these geometric features are correlated with
                model performance. Additionally, we observe that untrained models initially have different
                structures, but they rapidly converge during training. By leveraging our geometric analy-
                sis and differentiable tools, we can potentially design new and improved deep forecasting
                neural networks. This approach complements existing analysis studies and contributes to a
                better understanding of transformer models in the context of time series forecasting. Code
                is released at https://github.com/azencot-group/GATLM.'''
        
        text = pdf_handler.clean_(text)

        self.assertNotIn("\n",text)


if __name__ == "__main__":
    unittest.main()