# Changelog

## [2.0.0](https://github.com/pablofueros/mdapy-v2/compare/v0.1.1...v2.0.0) (2026-10-13)

First release of the maintained `mdapy-v2` distribution. The distribution
name changes from `ihc-mdapy`, while the Python import remains `mdapy`.

### Features

- Introduce the `DataColumn` API for declaring scalar and directional variables.
- Keep the tuple-based API available explicitly through `mdapy.legacy`.
- Add validation for column shapes, finite values, cluster counts, seed indices,
  and undefined deviations.

### Included fixes

- Include the NaN validation contributed by Álvaro Rodríguez in the historical
  but unpublished `v0.1.1` tag.
