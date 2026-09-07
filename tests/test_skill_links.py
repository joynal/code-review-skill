"""Keep bundled Markdown resources reachable after edits or packaging changes."""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class SkillLinksTests(unittest.TestCase):
  def test_local_markdown_links_resolve(self):
    paths = list(ROOT.glob('*.md'))
    for directory in ('reference', 'assets', 'docs'):
      paths.extend((ROOT / directory).glob('*.md'))

    for path in paths:
      text = path.read_text(encoding='utf-8')
      text = re.sub(
        r'^```.*?^```\s*$', '', text, flags=re.MULTILINE | re.DOTALL
      )
      for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
          continue
        destination = path.parent / unquote(parsed.path)
        with self.subTest(file=str(path.relative_to(ROOT)), link=target):
          self.assertTrue(destination.exists(), f'Missing {destination}')


if __name__ == '__main__':
  unittest.main()
