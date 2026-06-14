# Change Log
## [0.0.0] - 2023-11-29
### Init

## [0.0.1] - 2023-11-29
### Add
- Independent from sume MTamon's GitHub project to development and maintinance easier.
## [0.0.5] - 2026-06-12
### Fix
- `_VideoRIdx`: first iteration ignored `start` (no initial seek, `_current_idx` began at 0).
- `_VideoRIdx.__next__`: stop condition `== _stop` yielded frames `[0, stop)` instead of `[start, stop)`, and never stopped when `(stop - start)` was not a multiple of `step`. Now `>= _stop`.
- `_VideoRIdx.__next__`: `step > 1` seek double-added `_start`.
- `_VideoRIdx.__getitem__(int)`: restored the OpenCV constant `cv2.CAP_PROP_POS_FRAMES` instead of the saved current position, corrupting an ongoing iteration.
- `_VideoRIdx.__len__`: did not account for `step`.
- `patch_audio`: moviepy is now imported lazily and supports both moviepy 1.x (`moviepy.editor` / `set_audio`) and 2.x (`moviepy` / `with_audio`). With moviepy 2.x installed, `import easy_video` itself used to fail.
### Add
- `tests/test_video_reader.py`: regression tests for the fixes above (synthetic video with bit-pattern frame indices).

## [0.0.6] - 2026-06-14
### Fix
- Declare the `typing_extensions` runtime dependency (used by `open_type.py`). It was missing from requirements, so a clean install (without it pulled in transitively) failed to `import easy_video`.

## [0.0.7] - 2026-06-15
### Fix
- Relax pinned runtime dependencies (numpy / opencv / moviepy) from exact `==` to `>=` lower bounds. The previous `numpy==1.23.4` pin conflicted with opencv/moviepy (which pull in newer numpy) and made a clean install unresolvable on modern Python.
