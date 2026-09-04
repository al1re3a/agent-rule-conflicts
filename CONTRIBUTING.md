# Contributing

Focused bug fixes, new instruction-file formats, and carefully tested conflict
patterns are welcome.

1. Open an issue for behavior changes so the expected semantics are clear.
2. Create a focused branch and add a regression test.
3. Run `python -m unittest discover -s tests -v`.
4. Keep heuristics deterministic and explain false-positive tradeoffs in the PR.

Please do not add network calls or an LLM dependency to the default scanner.
