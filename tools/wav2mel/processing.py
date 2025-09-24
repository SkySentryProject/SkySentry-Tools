from pathlib import Path
import csv
import numpy as np
import soundfile as sf
import librosa
import matplotlib.pyplot as plt

def load_audio_mono(path: Path, target_sr: int, mono_strategy: str = "mean"):
    y, sr = sf.read(str(path), dtype="float32", always_2d=False)
    if y.ndim == 2:
        if mono_strategy == "mean":
            y = y.mean(axis=1)
        elif mono_strategy == "first":
            y = y[:, 0]
        else:
            raise ValueError("mono_strategy must be 'mean' or 'first'")
    if sr != target_sr:
        y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
        sr = target_sr
    return y.astype(np.float32), sr

def mel_log(y, sr, n_fft, hop, n_mels, fmin, fmax, center=True, top_db=80.0):
    M = librosa.feature.melspectrogram(
        y=y, sr=sr, n_fft=n_fft, hop_length=hop,
        n_mels=n_mels, fmin=fmin, fmax=fmax, power=2.0, center=center
    ).astype(np.float32)
    M_db = librosa.power_to_db(M, ref=np.max, top_db=top_db).astype(np.float32)
    return M_db  # shape: (n_mels, n_frames)

def frames_per_window(win_seconds, sr, hop):
    return max(1, int(round(win_seconds * sr / hop)))

def segment_mel(M_db, frames_win, frames_step, pad_last=False, pad_val=-80.0):
    n_mels, n_frames = M_db.shape
    segments = []
    starts = []
    for start in range(0, n_frames - frames_win + 1, frames_step):
        seg = M_db[:, start:start + frames_win]
        if seg.shape[1] == frames_win:
            segments.append(seg)
            starts.append(start)

    # incomplete tail
    last_start = (n_frames - frames_win + 1)
    if pad_last and last_start > 0 and last_start % frames_step != 0:
        start = n_frames - frames_win
        if start >= 0:
            seg = M_db[:, start:start + frames_win]
            if seg.shape[1] < frames_win:
                pad = np.full((n_mels, frames_win - seg.shape[1]), pad_val, dtype=np.float32)
                seg = np.concatenate([seg, pad], axis=1)
            segments.append(seg)
            starts.append(start)

    if not segments:
        return np.empty((0, n_mels, frames_win), dtype=np.float32), []
    return np.stack(segments, axis=0).astype(np.float32), starts

def save_png_mel(M_db, sr, hop, out_png: Path, title: str = "mel-log"):
    plt.figure(figsize=(10, 4))
    n_frames = M_db.shape[1]
    duration = (n_frames * hop) / sr
    extent = [0, duration, 0, M_db.shape[0]]  # time (s) x mel bins
    plt.imshow(M_db, origin="lower", aspect="auto", extent=extent)
    plt.xlabel("Time [s]")
    plt.ylabel("Mel bins")
    plt.title(title)
    plt.colorbar(label="dB (mel-log)")
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=150)
    plt.close()

def save_individual_pngs(chunks, starts, sr, hop, out_dir: Path, filename_prefix: str):
    """Save individual PNG files for each NPY segment"""
    n_mels, frames_win = chunks.shape[1], chunks.shape[2]
    duration_win = (frames_win * hop) / sr
    
    # Ensure output directory exists
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for i, (chunk, start) in enumerate(zip(chunks, starts)):
        start_time = (start * hop) / sr
        end_time = start_time + duration_win
        
        plt.figure(figsize=(8, 3))
        extent = [0, duration_win, 0, n_mels]
        plt.imshow(chunk, origin="lower", aspect="auto", extent=extent)
        plt.xlabel("Time [s]")
        plt.ylabel("Mel bins")
        plt.title(f"{filename_prefix} - Segment {i} ({start_time:.2f}s - {end_time:.2f}s)")
        plt.colorbar(label="dB (mel-log)")
        plt.tight_layout()
        
        png_path = out_dir / f"{filename_prefix}_segment_{i:04d}.png"
        plt.savefig(png_path, dpi=150)
        plt.close()

def process_file(wav_path: Path, out_dir: Path, args):
    y, sr = load_audio_mono(wav_path, args.sr, args.mono_strategy)
    M_db = mel_log(
        y, sr, args.n_fft, args.hop, args.n_mels,
        args.fmin, args.fmax, center=not args.no_center, top_db=args.top_db
    )

    if args.png:
        save_png_mel(M_db, sr, args.hop, out_dir / f"{wav_path.stem}_mel.png", title=wav_path.stem)

    frames_win = frames_per_window(args.win_seconds, sr, args.hop)
    frames_step = max(1, int(round(args.step_seconds * sr / args.hop)))

    chunks, starts = segment_mel(
        M_db, frames_win, frames_step, pad_last=args.pad_last, pad_val=args.pad_value
    )

    # Generate individual PNGs for each segment if requested
    if args.save_individual_png and chunks.shape[0] > 0:
        save_individual_pngs(chunks, starts, sr, args.hop, out_dir, wav_path.stem)

    # enforce dtype
    if args.dtype == "float16":
        chunks = chunks.astype(np.float16)
        M_db = M_db.astype(np.float16)
    else:
        chunks = chunks.astype(np.float32)
        M_db = M_db.astype(np.float32)

    out_dir.mkdir(parents=True, exist_ok=True)
    if args.save_full_mel:
        np.save(out_dir / f"{wav_path.stem}_mel_full.npy", M_db)

    index_rows = []
    if args.save_mode == "stack":
        if chunks.shape[0] > 0:
            stack_path = out_dir / f"{wav_path.stem}_mel_chunks.npy"
            np.save(stack_path, chunks)
            for i, start in enumerate(starts):
                start_s = (start * args.hop) / sr
                end_s = ((start + frames_win) * args.hop) / sr
                index_rows.append([str(wav_path), str(stack_path), i, start, start + frames_win, start_s, end_s])
    elif args.save_mode == "separate":
        for i, (seg, start) in enumerate(zip(chunks, starts)):
            seg_path = out_dir / f"{wav_path.stem}_chunk{i:04d}.npy"
            np.save(seg_path, seg)
            start_s = (start * args.hop) / sr
            end_s = ((start + frames_win) * args.hop) / sr
            index_rows.append([str(wav_path), str(seg_path), i, start, start + frames_win, start_s, end_s])
    else:
        raise SystemExit("--save-mode must be 'stack' or 'separate'")

    return sr, M_db.shape[1], frames_win, frames_step, index_rows

def write_index_csv(csv_path: Path, summary_rows, args):
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        import csv
        w = csv.writer(f)
        w.writerow([
            "source_wav", "npy_path_or_stack", "segment_idx",
            "start_frame", "end_frame", "start_time_s", "end_time_s",
            "sr", "n_fft", "hop", "n_mels", "fmin", "fmax",
            "win_seconds", "step_seconds"
        ])
        for row in summary_rows:
            (source, npy_path, i, start, end, start_s, end_s, sr, n_fft, hop,
             n_mels, fmin, fmax, win_sec, step_sec) = row
            w.writerow([source, npy_path, i, start, end, f"{start_s:.6f}", f"{end_s:.6f}",
                        sr, n_fft, hop, n_mels, fmin, fmax, win_sec, step_sec])
