"""Regression tests for observable diff inventory and CLI behavior."""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'pr-analyzer.py'
SPEC = importlib.util.spec_from_file_location('pr_analyzer', SCRIPT)
analyzer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = analyzer
SPEC.loader.exec_module(analyzer)


class DiffTests(unittest.TestCase):
  def test_hunk_content_that_looks_like_file_headers(self):
    diff = (
      'diff --git a/example.txt b/example.txt\n'
      '--- a/example.txt\n+++ b/example.txt\n'
      '@@ -1,2 +1,2 @@\n'
      '---old content\n+++new content\n unchanged\n'
    )
    (stats,) = analyzer.parse_diff(diff)
    self.assertEqual((stats.additions, stats.deletions), (1, 1))

  def test_unicode_line_separator_is_content(self):
    diff = (
      'diff --git a/example.txt b/example.txt\n'
      '--- a/example.txt\n+++ b/example.txt\n'
      '@@ -1 +1 @@\n-old\n+new\u2028still the same line\n'
    )
    (stats,) = analyzer.parse_diff(diff)
    self.assertEqual((stats.additions, stats.deletions), (1, 1))

  def test_deleted_file_and_missing_newline(self):
    diff = (
      'diff --git a/gone.py b/gone.py\n'
      'deleted file mode 100644\n'
      '--- a/gone.py\n+++ /dev/null\n'
      '@@ -1 +0,0 @@\n-print(1)\n'
      '\\ No newline at end of file\n'
    )
    (stats,) = analyzer.parse_diff(diff)
    self.assertEqual(stats.filename, 'gone.py')
    self.assertEqual((stats.additions, stats.deletions), (0, 1))

  def test_rename_reclassifies_destination(self):
    diff = (
      'diff --git a/helper.py b/test_helper.py\n'
      'similarity index 100%\n'
      'rename from helper.py\nrename to test_helper.py\n'
    )
    (stats,) = analyzer.parse_diff(diff)
    self.assertEqual(stats.filename, 'test_helper.py')
    self.assertTrue(stats.is_test)
    self.assertEqual((stats.additions, stats.deletions), (0, 0))

  def test_binary_path_with_spaces_and_b_prefix(self):
    diff = (
      'diff --git a/assets/a b/image.png b/assets/a b/image.png\n'
      'Binary files a/assets/a b/image.png and b/assets/a b/image.png differ\n'
    )
    (stats,) = analyzer.parse_diff(diff)
    self.assertEqual(stats.filename, 'assets/a b/image.png')
    self.assertEqual((stats.additions, stats.deletions), (0, 0))

  def test_file_classification(self):
    for filename in (
      'pkg/service_test.go',
      'src/UserTest.java',
      'ui/button.test.jsx',
      'ui/button.spec.mts',
      'tests/service.py',
      'pkg/test_service.py',
    ):
      with self.subTest(filename=filename):
        self.assertTrue(analyzer.is_test_file(filename))
    self.assertFalse(analyzer.is_test_file('contests/service.py'))
    self.assertEqual(analyzer.detect_language('module.cts'), 'TypeScript')
    self.assertEqual(analyzer.detect_language('styles.scss'), 'Sass')

  def test_rejects_combined_and_truncated_diffs(self):
    for diff in (
      'diff --cc example.py\n',
      'diff --combined example.py\n',
      'diff --git a/x b/x\n@@ -1,2 +1,2 @@\n-old\n+new\n',
    ):
      with self.subTest(diff=diff), self.assertRaises(ValueError):
        analyzer.parse_diff(diff)

  def test_empty_analysis_and_unrecognized_input(self):
    self.assertEqual(analyzer.analyze_pr('').total_files, 0)
    with self.assertRaises(ValueError):
      analyzer.analyze_pr('This is not a diff')

  def test_real_git_diff_agrees_with_numstat(self):
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)

      def git(*args):
        return subprocess.run(
          ['git', '-c', 'core.quotePath=true', *args],
          cwd=root,
          check=True,
          capture_output=True,
        ).stdout

      git('init', '-q')
      names = [
        'simple.py',
        'with space.ts',
        'quote"file.py',
        'tab\tfile.py',
        'café.py',
        'gone.py',
        'image.bin',
        'rename.py',
      ]
      for name in names:
        (root / name).write_bytes(
          b'\x00old' if name == 'image.bin' else b'old\n'
        )
      git('add', '.')
      for name in names:
        path = root / name
        if name == 'gone.py':
          path.unlink()
        elif name == 'rename.py':
          path.rename(root / 'test_renamed.py')
        elif name == 'image.bin':
          path.write_bytes(b'\x00new')
        else:
          path.write_bytes(b'++new\nsecond\n')
      (root / 'new.mts').write_text('export {};\n', encoding='utf-8')
      # Compare working tree to the staged baseline, avoiding a commit.
      diff = git(
        'diff',
        '--no-ext-diff',
        '--no-textconv',
        '--no-color',
        '--src-prefix=a/',
        '--dst-prefix=b/',
      ).decode('utf-8')
      files = analyzer.parse_diff(diff)
      expected = {}
      records = git('diff', '--numstat', '-z').split(b'\x00')
      for record in filter(None, records):
        additions, deletions, path = record.split(b'\t', 2)
        expected[path.decode('utf-8')] = (
          0 if additions == b'-' else int(additions),
          0 if deletions == b'-' else int(deletions),
        )
      self.assertEqual(
        {f.filename: (f.additions, f.deletions) for f in files},
        expected,
      )
      # Staging the new files makes Git emit actual addition headers.
      git('add', '-N', 'new.mts', 'test_renamed.py')
      diff = git(
        'diff',
        '--no-ext-diff',
        '--no-textconv',
        '--no-color',
        '--src-prefix=a/',
        '--dst-prefix=b/',
        '--no-renames',
      ).decode('utf-8')
      by_name = {f.filename: f for f in analyzer.parse_diff(diff)}
      self.assertEqual(by_name['new.mts'].additions, 1)
      self.assertTrue(by_name['test_renamed.py'].is_test)


class CLITests(unittest.TestCase):
  def run_cli(self, *args, input=''):
    return subprocess.run(
      [sys.executable, str(SCRIPT), *args],
      input=input,
      capture_output=True,
      text=True,
      check=False,
    )

  def test_empty_input_is_successful(self):
    result = self.run_cli()
    self.assertEqual(result.returncode, 0)
    self.assertIn('No changes', result.stdout)

  def test_bad_input_and_missing_file_fail_cleanly(self):
    for result in (
      self.run_cli(input='not a diff'),
      self.run_cli('--diff-file', '/nonexistent-review-diff'),
      self.run_cli(input='diff --cc merged.py\n'),
    ):
      self.assertNotEqual(result.returncode, 0)
      self.assertIn('error:', result.stderr)
      self.assertNotIn('Traceback', result.stderr)

  def test_saved_diff_and_stdin_match(self):
    diff = (
      'diff --git a/new.py b/new.py\n'
      '--- /dev/null\n+++ b/new.py\n'
      '@@ -0,0 +1 @@\n+print(1)\n'
    )
    with tempfile.TemporaryDirectory() as directory:
      path = Path(directory) / 'change.diff'
      path.write_text(diff, encoding='utf-8')
      saved = self.run_cli('--diff-file', str(path), '--stats')
      piped = self.run_cli('--stats', input=diff)
    self.assertEqual(saved.returncode, 0)
    self.assertEqual(piped.returncode, 0)
    self.assertEqual(saved.stdout, piped.stdout)
    self.assertIn('new.py (+1/-0)', saved.stdout)


if __name__ == '__main__':
  unittest.main()
