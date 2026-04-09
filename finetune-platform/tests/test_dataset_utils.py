import unittest

from scripts.dataset_utils import format_prompt, get_dataset_stats, split_dataset


class TestDatasetUtils(unittest.TestCase):
    def test_split_dataset_single_sample_keeps_train_non_empty(self):
        data = [{"id": 1}]
        train_data, eval_data = split_dataset(data, train_ratio=0.9, shuffle=False)
        self.assertEqual(len(train_data), 1)
        self.assertEqual(len(eval_data), 0)

    def test_split_dataset_two_samples_keeps_both_sides_non_empty(self):
        data = [{"id": 1}, {"id": 2}]
        train_data, eval_data = split_dataset(data, train_ratio=0.9, shuffle=False)
        self.assertEqual(len(train_data), 1)
        self.assertEqual(len(eval_data), 1)

    def test_sharegpt_stats_and_preview(self):
        sample = {
            "conversations": [
                {"from": "human", "value": "你好"},
                {"from": "gpt", "value": "你好！"},
            ]
        }
        stats = get_dataset_stats([sample], format_type="sharegpt")
        self.assertEqual(stats["valid_samples"], 1)
        self.assertGreater(stats["avg_instruction_len"], 0)
        self.assertGreater(stats["avg_output_len"], 0)

        preview = format_prompt(sample, format_type="sharegpt")
        self.assertIn("human: 你好", preview)
        self.assertIn("gpt: 你好！", preview)


if __name__ == "__main__":
    unittest.main()
