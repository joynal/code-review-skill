#!/usr/bin/env python3
"""
PR Analyzer - Inventory a Git unified diff using size-based heuristics.

Requires Python 3.10+. No third-party dependencies.

Usage:
    python3 pr-analyzer.py [--diff-file FILE] [--stats]

    Or pipe diff directly:
    git diff --no-color BASE...HEAD | python3 pr-analyzer.py
"""

import argparse
import codecs
import re
import sys
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class FileStats:
  """Statistics for a single file."""

  filename: str
  additions: int = 0
  deletions: int = 0
  is_test: bool = False
  is_config: bool = False
  language: str = 'unknown'


@dataclass
class PRAnalysis:
  """Complete PR analysis results."""

  total_files: int
  total_additions: int
  total_deletions: int
  files: list[FileStats]
  complexity_score: float
  size_category: str
  estimated_review_time: int
  risk_factors: list[str]
  suggestions: list[str]


def detect_language(filename: str) -> str:
  """Detect programming language from filename."""
  extensions = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript/React',
    '.jsx': 'JavaScript/React',
    '.mjs': 'JavaScript',
    '.cjs': 'JavaScript',
    '.mts': 'TypeScript',
    '.cts': 'TypeScript',
    '.go': 'Go',
    '.java': 'Java',
    '.rb': 'Ruby',
    '.sql': 'SQL',
    '.md': 'Markdown',
    '.json': 'JSON',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.toml': 'TOML',
    '.css': 'CSS',
    '.scss': 'Sass',
    '.sass': 'Sass',
    '.less': 'Less',
    '.html': 'HTML',
    '.jsonnet': 'Configuration Language',
  }
  for ext, lang in extensions.items():
    if filename.endswith(ext):
      return lang
  return 'unknown'


def is_test_file(filename: str) -> bool:
  """Check if file is a test file."""
  test_patterns = [
    r'(^|/)test_[^/]*\.py$',
    r'_test\.(py|go)$',
    r'\.(test|spec)\.(js|jsx|ts|tsx|mjs|cjs|mts|cts)$',
    r'(^|/)(tests?|__tests__)/',
    r'(^|/)[^/]*(Test|Tests)\.java$',
  ]
  return any(re.search(p, filename) for p in test_patterns)


def is_config_file(filename: str) -> bool:
  """Check if file is a configuration file."""
  config_patterns = [
    r'\.env',
    r'config\.',
    r'\.json$',
    r'\.yaml$',
    r'\.yml$',
    r'\.toml$',
    r'Cargo\.toml$',
    r'package\.json$',
    r'tsconfig\.json$',
  ]
  return any(re.search(p, filename) for p in config_patterns)


def decode_git_path(path: str) -> str:
  """Decode Git's C-quoted filenames, including octal UTF-8 bytes."""
  if path.startswith('"'):
    if not path.endswith('"'):
      raise ValueError('Unterminated quoted Git path')
    decoded, _ = codecs.escape_decode(path[1:-1].encode('utf-8'))
    return decoded.decode('utf-8', errors='surrogateescape')
  return path


def set_filename(stats: FileStats, filename: str) -> None:
  """Keep classifications aligned when extended headers supply a path."""
  stats.filename = filename
  stats.language = detect_language(filename)
  stats.is_test = is_test_file(filename)
  stats.is_config = is_config_file(filename)


def parse_diff(diff_content: str) -> list[FileStats]:
  """Parse standard a/ and b/ Git unified diffs; reject combined diffs."""
  files = []
  current_file = None
  old_remaining = new_remaining = 0
  hunk_pattern = re.compile(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')
  path_pattern = re.compile(
    r'^diff --git ("(?:[^"\\]|\\.)*"|a/.*?) ("(?:[^"\\]|\\.)*"|b/.*)$'
  )

  for line in diff_content.split('\n'):
    if line.startswith(('diff --cc ', 'diff --combined ', '@@@ ')):
      raise ValueError(
        'Combined merge diffs are unsupported; compare two revisions'
      )
    if line.startswith('diff --git '):
      if old_remaining or new_remaining:
        raise ValueError('Truncated diff hunk')
      if current_file:
        files.append(current_file)
      # Equal unquoted paths can contain spaces and even " b/".
      same_path = re.fullmatch(r'diff --git a/(.+) b/\1', line)
      match = path_pattern.fullmatch(line)
      if same_path:
        filename = same_path.group(1)
      elif match:
        destination = decode_git_path(match.group(2))
        if not destination.startswith('b/'):
          raise ValueError('Expected standard a/ and b/ Git path prefixes')
        filename = destination[2:]
      else:
        raise ValueError(
          'Invalid Git diff header; use standard a/ and b/ prefixes'
        )
      current_file = FileStats(filename=filename)
      set_filename(current_file, filename)
    elif current_file is not None:
      if line.startswith('\\ No newline at end of file'):
        continue
      if old_remaining or new_remaining:
        if line.startswith('+'):
          current_file.additions += 1
          new_remaining -= 1
        elif line.startswith('-'):
          current_file.deletions += 1
          old_remaining -= 1
        elif line.startswith(' '):
          old_remaining -= 1
          new_remaining -= 1
        else:
          raise ValueError('Invalid or truncated diff hunk')
        if old_remaining < 0 or new_remaining < 0:
          raise ValueError('Diff hunk counts do not match its contents')
      elif line.startswith('@@'):
        hunk = hunk_pattern.match(line)
        if hunk is None:
          raise ValueError('Invalid unified diff hunk header')
        old_remaining = int(hunk.group(2) or '1')
        new_remaining = int(hunk.group(4) or '1')
      elif line.startswith('+++ '):
        destination = decode_git_path(line[4:].split('\t', 1)[0])
        if destination != '/dev/null':
          if not destination.startswith('b/'):
            raise ValueError('Expected b/ destination prefix')
          set_filename(current_file, destination[2:])
      elif line.startswith('rename to '):
        set_filename(current_file, decode_git_path(line[len('rename to ') :]))
      elif line.startswith('copy to '):
        set_filename(current_file, decode_git_path(line[len('copy to ') :]))

  if old_remaining or new_remaining:
    raise ValueError('Truncated diff hunk')
  if current_file:
    files.append(current_file)

  return files


def calculate_complexity(files: list[FileStats]) -> float:
  """Calculate a size-based review heuristic (not semantic complexity)."""
  if not files:
    return 0.0

  total_changes = sum(f.additions + f.deletions for f in files)

  # Base complexity from size
  size_factor = min(total_changes / 1000, 1.0)

  # Factor for number of files
  file_factor = min(len(files) / 20, 1.0)

  # Factor for non-test code ratio
  test_lines = sum(f.additions + f.deletions for f in files if f.is_test)
  non_test_ratio = 1 - (test_lines / max(total_changes, 1))

  # Factor for language diversity
  languages = {f.language for f in files if f.language != 'unknown'}
  lang_factor = min(len(languages) / 5, 1.0)

  complexity = (
    size_factor * 0.4
    + file_factor * 0.2
    + non_test_ratio * 0.2
    + lang_factor * 0.2
  )

  return round(complexity, 2)


def categorize_size(total_changes: int) -> str:
  """Categorize PR size."""
  if total_changes < 50:
    return 'XS (Extra Small)'
  elif total_changes < 200:
    return 'S (Small)'
  elif total_changes < 400:
    return 'M (Medium)'
  elif total_changes < 800:
    return 'L (Large)'
  else:
    return 'XL (Extra Large) - Consider splitting'


def estimate_review_time(files: list[FileStats], complexity: float) -> int:
  """Estimate review time in minutes."""
  total_changes = sum(f.additions + f.deletions for f in files)

  # Base time: ~1 minute per 20 lines
  base_time = total_changes / 20

  # Adjust for complexity
  adjusted_time = base_time * (1 + complexity)

  # Minimum 5 minutes, maximum 120 minutes
  return max(5, min(120, int(adjusted_time)))


def identify_risk_factors(files: list[FileStats]) -> list[str]:
  """Identify potential risk factors in the PR."""
  risks = []

  total_changes = sum(f.additions + f.deletions for f in files)
  test_changes = sum(f.additions + f.deletions for f in files if f.is_test)

  # Large PR
  if total_changes > 400:
    risks.append('Large PR (>400 lines) - harder to review thoroughly')

  # No tests
  if test_changes == 0 and total_changes > 50:
    risks.append('No test changes - verify test coverage')

  # Security-sensitive files
  security_patterns = [
    '.env',
    'auth',
    'security',
    'password',
    'token',
    'secret',
  ]
  for f in files:
    if any(p in f.filename.lower() for p in security_patterns):
      risks.append(f'Security-sensitive file: {f.filename}')
      break

  # Database changes
  for f in files:
    if 'migration' in f.filename.lower() or f.language == 'SQL':
      risks.append('Database changes detected - review carefully')
      break

  # Config changes
  config_files = [f for f in files if f.is_config]
  if config_files:
    risks.append(f'Configuration changes in {len(config_files)} file(s)')

  return risks


def generate_suggestions(
  files: list[FileStats], complexity: float, risks: list[str]
) -> list[str]:
  """Generate review suggestions."""
  suggestions = []

  total_changes = sum(f.additions + f.deletions for f in files)

  if total_changes > 800:
    suggestions.append(
      'Consider splitting this PR into smaller, focused changes'
    )

  if complexity > 0.7:
    suggestions.append('High complexity - allocate extra review time')
    suggestions.append('Consider pair reviewing for critical sections')

  if 'No test changes' in str(risks):
    suggestions.append(
      'Inspect existing tests for changed behavior; diff counts do not measure coverage'
    )

  # Language-specific suggestions
  languages = {f.language for f in files}
  if 'TypeScript' in languages or 'TypeScript/React' in languages:
    suggestions.append("Check for proper type usage (avoid 'any')")
  if 'SQL' in languages:
    suggestions.append('Review for SQL injection and query performance')

  if not suggestions:
    suggestions.append('Standard review process should suffice')

  return suggestions


def analyze_pr(diff_content: str) -> PRAnalysis:
  """Perform complete PR analysis."""
  files = parse_diff(diff_content)
  if diff_content.strip() and not files:
    raise ValueError('No Git unified diff found')

  total_additions = sum(f.additions for f in files)
  total_deletions = sum(f.deletions for f in files)
  total_changes = total_additions + total_deletions

  complexity = calculate_complexity(files)
  risks = identify_risk_factors(files)
  suggestions = generate_suggestions(files, complexity, risks)

  return PRAnalysis(
    total_files=len(files),
    total_additions=total_additions,
    total_deletions=total_deletions,
    files=files,
    complexity_score=complexity,
    size_category=categorize_size(total_changes),
    estimated_review_time=estimate_review_time(files, complexity),
    risk_factors=risks,
    suggestions=suggestions,
  )


def print_analysis(analysis: PRAnalysis, show_files: bool = False):
  """Print analysis results."""
  print('\n' + '=' * 60)
  print('PR ANALYSIS REPORT')
  print(
    'Size-based heuristics only; not measured complexity, coverage, or merge criteria.'
  )
  print('=' * 60)

  print('\n📊 SUMMARY')
  print(f'   Files changed: {analysis.total_files}')
  print(f'   Additions: +{analysis.total_additions}')
  print(f'   Deletions: -{analysis.total_deletions}')
  print(
    f'   Total changes: {analysis.total_additions + analysis.total_deletions}'
  )

  print(f'\n📏 SIZE: {analysis.size_category}')
  print(f'   Complexity score: {analysis.complexity_score}/1.0')
  print(f'   Estimated review time: ~{analysis.estimated_review_time} minutes')

  if analysis.risk_factors:
    print('\n⚠️  RISK FACTORS:')
    for risk in analysis.risk_factors:
      print(f'   • {risk}')

  print('\n💡 SUGGESTIONS:')
  for suggestion in analysis.suggestions:
    print(f'   • {suggestion}')

  if show_files:
    print('\n📁 FILES:')
    # Group by language
    by_lang: dict[str, list[FileStats]] = defaultdict(list)
    for f in analysis.files:
      by_lang[f.language].append(f)

    for lang, lang_files in sorted(by_lang.items()):
      print(f'\n   [{lang}]')
      for f in lang_files:
        prefix = '🧪' if f.is_test else '⚙️' if f.is_config else '📄'
        print(f'   {prefix} {f.filename} (+{f.additions}/-{f.deletions})')

  print('\n' + '=' * 60)


def main():
  parser = argparse.ArgumentParser(
    description='Inventory a Git unified diff (size-based heuristics)'
  )
  parser.add_argument('--diff-file', '-f', help='Path to diff file')
  parser.add_argument(
    '--stats', '-s', action='store_true', help='Show file details'
  )
  args = parser.parse_args()

  # Read diff from file or stdin
  try:
    if args.diff_file:
      with open(
        args.diff_file, encoding='utf-8', errors='surrogateescape'
      ) as f:
        diff_content = f.read()
    elif not sys.stdin.isatty():
      diff_content = sys.stdin.read()
    else:
      parser.error('Pass --diff-file FILE or pipe a Git unified diff on stdin')
  except (OSError, UnicodeError) as exc:
    parser.error(str(exc))

  if not diff_content.strip():
    print('No changes to analyze')
    return

  try:
    analysis = analyze_pr(diff_content)
  except (ValueError, UnicodeError) as exc:
    parser.error(str(exc))
  print_analysis(analysis, show_files=args.stats)


if __name__ == '__main__':
  main()
