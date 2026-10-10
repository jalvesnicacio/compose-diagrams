import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from compose_diagrams import ComposeError, load
from compose_diagrams.cli import main
from compose_diagrams.web import create_app


class ServiceShapeTests(unittest.TestCase):
    def test_load_rejects_non_mapping_service_definitions(self):
        for value in ("hello", "null", "[]"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    ComposeError, "service 'web' must be a mapping"
                ):
                    load(f"services:\n  web: {value}\n")

    def test_cli_reports_service_validation_error(self):
        with tempfile.TemporaryDirectory() as directory:
            compose_file = Path(directory) / "compose.yaml"
            compose_file.write_text("services:\n  web: hello\n", encoding="utf-8")

            with patch("compose_diagrams.cli.shutil.which", return_value="dot"):
                with self.assertRaises(SystemExit) as raised:
                    main([str(compose_file)])

        self.assertEqual(
            raised.exception.code,
            f"error: {compose_file}: service 'web' must be a mapping",
        )

    def test_web_reports_service_validation_error_as_bad_request(self):
        response = create_app().test_client().post(
            "/render", json={"compose": "services:\n  web: hello\n"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "service 'web' must be a mapping"})


if __name__ == "__main__":
    unittest.main()
