# AS_PATH Validation Algorithm

This python project has five different implementations of the `AS_PATH` verification algorithm.

- `simplified.py` unified algorithm but with modified hop-function
- `simplified2.py` unified algorithm but without the modified hop-function
- `draft.py` implementation of the upstream and downstream formal procedure as described in draft-ietf-sidrops-aspa-verification-16
- `optimized.py` optimized algorithm which doesn't perform any aspa look-up twice
- `optimizedZeroBased.py`optimized algorithm which doesn't perform any aspa look-up twice and reversed `AS_PATH` (hence origin AS is at index N-1)

`test.py` contains different test cases which are used to check for identical behavior.
