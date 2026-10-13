"""Lightweight smoke tests for the pure helpers behind BuildWithCrew.

Run with:
    python -m unittest discover -s tests
"""

import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils.helpers as helpers
from utils.parsing import extract_code, parse_review, safe_block


class ParseReviewTests(unittest.TestCase):
    SAMPLE = (
        "BUGS:\n- off by one error\n\n"
        "OPTIMIZATIONS:\n- cache results\n\n"
        "BEST PRACTICES:\n- add type hints\n\n"
        "CORRECTED CODE:\n```python\nprint('ok')\n```\n"
    )

    def test_all_sections_parsed(self):
        sections = parse_review(self.SAMPLE)
        self.assertEqual(
            set(sections),
            {"BUGS", "OPTIMIZATIONS", "BEST PRACTICES", "CORRECTED CODE"},
        )
        self.assertIn("off by one", sections["BUGS"])
        self.assertIn("cache results", sections["OPTIMIZATIONS"])

    def test_empty_input_returns_empty(self):
        self.assertEqual(parse_review(""), {})
        self.assertEqual(parse_review(None), {})


class ExtractCodeTests(unittest.TestCase):
    def test_fenced_code(self):
        language, code = extract_code("```python\nx = 1\n```")
        self.assertEqual(language, "python")
        self.assertEqual(code, "x = 1")

    def test_unfenced_code(self):
        language, code = extract_code("x = 1")
        self.assertEqual(language, "text")
        self.assertEqual(code, "x = 1")

    def test_empty_section(self):
        self.assertEqual(extract_code(""), ("text", ""))


class SafeBlockTests(unittest.TestCase):
    def test_html_is_escaped(self):
        out = safe_block("<script>alert(1)</script>")
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)

    def test_newlines_become_breaks(self):
        self.assertEqual(safe_block("a\nb"), "a<br>b")

    def test_empty(self):
        self.assertEqual(safe_block(""), "")


class DatabaseTests(unittest.TestCase):
    def test_connection_is_closed_after_write(self):
        fake = mock.MagicMock()
        with mock.patch.object(helpers, "_connect", return_value=fake):
            helpers.save_to_history("idea", "Tester", "output")
        fake.execute.assert_called_once()
        fake.commit.assert_called_once()
        fake.close.assert_called_once()

    def test_connection_closed_after_read(self):
        fake = mock.MagicMock()
        fake.execute.return_value.fetchall.return_value = []
        with mock.patch.object(helpers, "_connect", return_value=fake):
            self.assertEqual(helpers.get_history(), [])
        fake.close.assert_called_once()


def _completion(content, finish_reason):
    return types.SimpleNamespace(
        choices=[
            types.SimpleNamespace(
                finish_reason=finish_reason,
                message=types.SimpleNamespace(content=content),
            )
        ]
    )


class GetAiResponseTests(unittest.TestCase):
    def _call(self, completion):
        with mock.patch.object(helpers, "get_client", return_value=object()):
            with mock.patch.object(
                helpers, "_create_completion", return_value=completion
            ):
                return helpers.get_ai_response("system", "user")

    def test_normal_response_passthrough(self):
        self.assertEqual(self._call(_completion("full answer", "stop")), "full answer")

    def test_truncated_response_returned_with_note(self):
        result = self._call(_completion("partial answer", "length"))
        self.assertIn("partial answer", result)
        self.assertIn("truncated", result.lower())

    def test_empty_truncated_response_raises(self):
        with self.assertRaises(RuntimeError):
            self._call(_completion("", "length"))


class ModelResolutionTests(unittest.TestCase):
    def test_default_model(self):
        with mock.patch.object(helpers, "_secret", return_value=None):
            with mock.patch.dict(helpers.os.environ, {}, clear=True):
                self.assertEqual(helpers._resolve_model(), helpers.DEFAULT_MODEL)

    def test_env_override(self):
        with mock.patch.object(helpers, "_secret", return_value=None):
            with mock.patch.dict(helpers.os.environ, {"GROQ_MODEL": "custom/model"}):
                self.assertEqual(helpers._resolve_model(), "custom/model")

    def test_secret_takes_priority(self):
        with mock.patch.object(helpers, "_secret", return_value="secret/model"):
            with mock.patch.dict(helpers.os.environ, {"GROQ_MODEL": "env/model"}):
                self.assertEqual(helpers._resolve_model(), "secret/model")

    def test_reasoning_effort_can_be_disabled(self):
        with mock.patch.object(helpers, "_secret", return_value=None):
            with mock.patch.dict(helpers.os.environ, {"GROQ_REASONING_EFFORT": "off"}):
                self.assertIsNone(helpers._resolve_reasoning_effort())

    def test_reasoning_effort_default(self):
        with mock.patch.object(helpers, "_secret", return_value=None):
            with mock.patch.dict(helpers.os.environ, {}, clear=True):
                self.assertEqual(
                    helpers._resolve_reasoning_effort(), helpers.REASONING_EFFORT
                )


if __name__ == "__main__":
    unittest.main()
