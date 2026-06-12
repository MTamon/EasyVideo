"""Regression tests for _VideoRIdx range bugs (v0.0.5).

Covers the 4-bug set fixed in 0.0.5:
  1. first iteration ignored `start` (no seek, `_current_idx = 0`)
  2. stop condition `== _stop` yielded `stop` frames from frame 0
  3. `__getitem__(int)` restored an OpenCV constant instead of the
     current position
  4. `step > 1` double-added `_start` when seeking
plus `__len__` not accounting for `step`.

Each frame of the synthetic video encodes its frame index as 8 high
contrast horizontal stripes (one per bit, 0 or 255), so the index
survives lossy encoding and is recovered by thresholding stripe means.
"""

import os
import tempfile

import cv2
import numpy as np

from easy_video import VideoReader, VideoWriter

N_FRAMES = 50
FPS = 25.0
SIZE_WH = (64, 64)


_STRIPE_H = SIZE_WH[1] // 8


def _encode_frame(idx: int) -> np.ndarray:
    frame = np.zeros((SIZE_WH[1], SIZE_WH[0], 3), dtype=np.uint8)
    for bit in range(8):
        if (idx >> bit) & 1:
            frame[bit * _STRIPE_H : (bit + 1) * _STRIPE_H] = 255
    return frame


def _make_video(path: str) -> None:
    writer = VideoWriter(path, fps=FPS)
    writer.write([_encode_frame(i) for i in range(N_FRAMES)])
    writer.close()


def _decode_idx(frame: np.ndarray) -> int:
    idx = 0
    for bit in range(8):
        stripe = frame[bit * _STRIPE_H : (bit + 1) * _STRIPE_H]
        if float(stripe.mean()) > 127.0:
            idx |= 1 << bit
    return idx


_TMP_DIR = tempfile.mkdtemp(prefix="easy_video_test_")
_VIDEO_PATH = os.path.join(_TMP_DIR, "synthetic.mp4")
_make_video(_VIDEO_PATH)


def test_full_iteration_unchanged():
    """Equivalence: default reading (start=0, step=1) must keep yielding
    all frames in order, as 0.0.4 already did."""
    reader = VideoReader(_VIDEO_PATH)
    indices = [_decode_idx(f) for f in reader]
    assert indices == list(range(N_FRAMES)), indices


def test_trime_time_respects_start():
    """Bug 1+2: trime_time(10/fps, 20/fps) must yield frames [10..19]."""
    reader = VideoReader(_VIDEO_PATH)
    clip = reader.trime_time(10 / FPS, 20 / FPS)
    indices = [_decode_idx(f) for f in clip]
    assert indices == list(range(10, 20)), indices


def test_iteration_is_repeatable():
    """_reset after StopIteration: a second pass must equal the first."""
    reader = VideoReader(_VIDEO_PATH)
    clip = reader.trime_frame(5, 15)
    first = [_decode_idx(f) for f in clip]
    second = [_decode_idx(f) for f in clip]
    assert first == second == list(range(5, 15)), (first, second)


def test_step_slice():
    """Bug 4: step>1 must yield start, start+step, ... < stop."""
    reader = VideoReader(_VIDEO_PATH)
    clip = reader[10:20:2]
    indices = [_decode_idx(f) for f in clip]
    assert indices == [10, 12, 14, 16, 18], indices


def test_step_slice_non_multiple_range():
    """Bug 2 (step>1 overrun): `==` never matched when the range is not a
    multiple of step; `>=` must stop at the right frame."""
    reader = VideoReader(_VIDEO_PATH)
    clip = reader[0:10:3]
    indices = [_decode_idx(f) for f in clip]
    assert indices == [0, 3, 6, 9], indices


def test_len_accounts_for_step():
    reader = VideoReader(_VIDEO_PATH)
    assert len(reader[10:20:2]) == 5
    assert len(reader[0:10:3]) == 4
    assert len(reader[5:15:1]) == 10
    assert len(reader[10:10:1]) == 0


def test_getitem_preserves_iteration_position():
    """Bug 3: random access during iteration must not corrupt the
    iterator position."""
    reader = VideoReader(_VIDEO_PATH)
    clip = reader.trime_frame(20, 30)
    it = iter(clip)
    head = [_decode_idx(next(it)) for _ in range(3)]
    _ = clip[0]  # random access in the middle of iteration
    tail = [_decode_idx(f) for f in it]
    assert head + tail == list(range(20, 30)), (head, tail)


def test_getitem_int():
    reader = VideoReader(_VIDEO_PATH)
    assert _decode_idx(reader[42]) == 42


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as exc:
                failed += 1
                print(f"FAIL {name}: {exc}")
    raise SystemExit(failed)
