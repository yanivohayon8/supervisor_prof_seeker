import unittest
from src.dataset_synthesize import synthesizer

class TestLunaryDataset(unittest.TestCase):

    def test_read_dataset_from_file_(self):
        desired_record = 24

        for thread in synthesizer.read_dataset_from_file_():
            
            if desired_record == 0:

                for mess in thread["messages"]:
                    print(f"**************** {mess["role"]} ****************")
                    print(mess["content"])

                break
            else:
                desired_record-=1

    def test_get_url(self):
        url = synthesizer.get_url_("runs")
        self.assertTrue(url.endswith("/runs"))

    def test_get_runs_compiles(self):
        pages = 0
        for runs in synthesizer.get_runs():
            self.assertIsInstance(runs,list)
            self.assertGreater(len(runs),0)
            pages+=1
        
        self.assertGreater(pages,0)

    
    def test_read_dataset(self):
        count = 0

        for thread in synthesizer.read_dataset():
            count+=1

            for mess in thread["messages"]:
                print(f"**************** {mess["role"]} ****************")
                print(mess["content"])

            break
        
        self.assertGreater(count,0)
        
if __name__ == "__main__":
    unittest.main()