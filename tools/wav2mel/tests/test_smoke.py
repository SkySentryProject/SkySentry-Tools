import numpy as np
from tools.wav2mel.processing import segment_mel

def test_segment_shapes():
    # fake mel: 64 bins, 100 frames
    M = np.random.randn(64, 100).astype(np.float32)
    chunks, starts = segment_mel(M, frames_win=10, frames_step=5, pad_last=False)
    assert chunks.ndim == 3
    assert chunks.shape[1] == 64
    assert chunks.shape[2] == 10
    assert len(starts) == chunks.shape[0]
