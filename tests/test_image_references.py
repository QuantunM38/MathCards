"""Offline checks: run python -m unittest discover -s tests -v."""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'https://raw.githubusercontent.com/QuantunM38/MathCards/main/'


def image_path(url):
    if not isinstance(url, str) or not url.startswith(PREFIX):
        raise ValueError('Expected the existing MathCards raw main URL')
    path = url[len(PREFIX):]
    parts = path.split('/')
    if len(parts) != 2 or parts[0] != 'image' or not parts[1]:
        raise ValueError('Expected a direct image/ file')
    if any(c in path for c in ('?', '#', '%', '\\')) or parts[1] in ('.', '..'):
        raise ValueError('Ambiguous image path')
    return path


def exact_file(root, relative, tracked):
    # Git membership and directory enumeration are case-sensitive string checks,
    # even when the host filesystem resolves names without regard to case.
    if relative not in tracked:
        return False
    current = root
    for part in relative.split('/'):
        if not current.is_dir() or part not in {p.name for p in current.iterdir()}:
            return False
        current = current / part
        if current.is_symlink():
            return False
    return current.is_file()


class ImageReferences(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracked = set(subprocess.check_output(
            ['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0'))

    def test_all_metadata_references(self):
        metadata = sorted(p for p in self.tracked if p.startswith('metadata/') and p.endswith('.json'))
        self.assertEqual(metadata, [f'metadata/{i:04}.json' for i in range(1, 11)])
        for name in metadata:
            with self.subTest(metadata=name):
                data = json.loads((ROOT / name).read_text(encoding='utf-8'))
                path = image_path(data['image'])
                self.assertTrue(exact_file(ROOT, path, self.tracked), f'Missing exact tracked file: {path}')

    def test_original_files_unchanged(self):
        manifest = json.loads((ROOT / 'tests/original_sha256.json').read_text())
        self.assertEqual(len(manifest['files']), 21)
        for name, expected in manifest['files'].items():
            with self.subTest(file=name):
                self.assertTrue(exact_file(ROOT, name, self.tracked))
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected)

    def test_compatibility_copies_are_identical(self):
        for i in range(2, 11):
            with self.subTest(card=i):
                old, new = f'image/{i:04}.PNG', f'image/{i:04}.png'
                self.assertTrue(exact_file(ROOT, new, self.tracked))
                self.assertEqual((ROOT / old).read_bytes(), (ROOT / new).read_bytes())


class ValidatorRegression(unittest.TestCase):
    def test_wrong_case_is_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'image').mkdir()
            (root / 'image/0002.PNG').write_bytes(b'image')
            self.assertFalse(exact_file(root, 'image/0002.png', {'image/0002.PNG'}))
            self.assertFalse(exact_file(root, 'image/0002.png', {'image/0002.png'}))
            self.assertTrue(exact_file(root, 'image/0002.PNG', {'image/0002.PNG'}))
            self.assertFalse(exact_file(root, 'image/0002.PNG', set()))

    def test_invalid_urls_are_rejected(self):
        for url in (None, '', PREFIX.replace('https:', 'http:') + 'image/0002.png',
                    PREFIX + '../image/0002.png', PREFIX + 'image/../0002.png',
                    PREFIX + 'image/0002.png?raw=1', PREFIX + 'image/%30%30%30%32.png',
                    PREFIX + 'image/..', PREFIX + 'image/0002.png#fragment'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                image_path(url)

    def test_existing_url_maps_exactly(self):
        self.assertEqual(image_path(PREFIX + 'image/0002.png'), 'image/0002.png')


if __name__ == '__main__':
    unittest.main()
