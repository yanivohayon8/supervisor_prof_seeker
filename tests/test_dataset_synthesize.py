import unittest
from src.dataset_synthesize import synthesizer

class TestLunaryDataset(unittest.TestCase):

    def test_read_dataset_from_file_(self):
        desired_record = 24

        for conversation in synthesizer.read_dataset_from_file_():
            
            if desired_record == 0:

                for mess in conversation["messages"]:
                    print(f"**************** {mess["role"]} ****************")
                    print(mess["content"])

                break
            else:
                desired_record-=1
if __name__ == "__main__":
    unittest.main()