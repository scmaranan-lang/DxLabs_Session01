import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app import NamePickerHandler, choose_name, normalize_names


class NameValidationTests(unittest.TestCase):
    def test_normalizes_whitespace(self):
        self.assertEqual(normalize_names(["  Ada  ", "Lin"]), ["Ada", "Lin"])

    def test_rejects_empty_names(self):
        with self.assertRaisesRegex(ValueError, "between 1 and 500"):
            normalize_names([])
        with self.assertRaisesRegex(ValueError, "cannot be blank"):
            normalize_names(["  "])

    def test_rejects_invalid_names(self):
        with self.assertRaisesRegex(ValueError, "must be text"):
            normalize_names(["Ada", 5])
        with self.assertRaisesRegex(ValueError, "100 characters or fewer"):
            normalize_names(["A" * 101])
        with self.assertRaisesRegex(ValueError, "between 1 and 500"):
            normalize_names(["Ada"] * 501)

    def test_pick_returns_one_of_the_names(self):
        self.assertIn(choose_name(["Ada", "Lin"]), ["Ada", "Lin"])


class NamePickerEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), NamePickerHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()

    def post_json(self, payload):
        request = Request(
            f"{self.base_url}/api/pick",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return urlopen(request)

    def test_serves_picker_page_and_assets(self):
        with urlopen(self.base_url) as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b"Let fate", response.read())

        with urlopen(f"{self.base_url}/static/app.js") as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b"number = 5", response.read())

    def test_pick_endpoint_returns_a_name(self):
        with self.post_json({"names": ["Ada", "Lin"]}) as response:
            self.assertEqual(response.status, 200)
            self.assertIn(json.loads(response.read())["name"], ["Ada", "Lin"])

    def test_pick_endpoint_rejects_invalid_input(self):
        with self.assertRaises(HTTPError) as error:
            self.post_json({"names": []})
        self.assertEqual(error.exception.code, 400)
        self.assertEqual(json.loads(error.exception.read())["error"], "Enter between 1 and 500 names.")
        error.exception.close()

    def test_pick_endpoint_rejects_malformed_json(self):
        request = Request(
            f"{self.base_url}/api/pick",
            data=b"{",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(HTTPError) as error:
            urlopen(request)
        self.assertEqual(error.exception.code, 400)
        self.assertEqual(json.loads(error.exception.read())["error"], "Request body must be valid JSON.")
        error.exception.close()


if __name__ == "__main__":
    unittest.main()
