import unittest

import torch

from scripts.model_utils import generate_response


class _FakeInputs(dict):
    def to(self, _device):
        return self


class _FakeTokenizer:
    pad_token_id = 0
    eos_token_id = 2

    def __call__(self, _prompt, return_tensors="pt"):
        assert return_tensors == "pt"
        return _FakeInputs({"input_ids": torch.tensor([[1, 2, 3]])})

    def decode(self, token_ids, skip_special_tokens=True):
        assert skip_special_tokens is True
        return ",".join(str(int(x)) for x in token_ids.tolist())


class _FakeModel:
    device = "cpu"

    def generate(self, **_kwargs):
        return torch.tensor([[1, 2, 3, 4, 5]])


class TestModelUtils(unittest.TestCase):
    def test_generate_response_decodes_only_new_tokens(self):
        response = generate_response(
            model=_FakeModel(),
            tokenizer=_FakeTokenizer(),
            prompt="unused",
            max_new_tokens=8,
        )
        self.assertEqual(response, "4,5")


if __name__ == "__main__":
    unittest.main()
