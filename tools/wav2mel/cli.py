from pathlib import Path
from tqdm import tqdm
import argparse

from .processing import process_file, write_index_csv

def collect_wavs(path: Path):
    if path.is_dir():
        return sorted(p for p in path.rglob("*.wav"))
    return [path] if path.is_file() and path.suffix.lower() == ".wav" else []

def build_parser():
    ap = argparse.ArgumentParser(
        prog="wav2mel",
        description="WAV → mel-log (full PNG) + NPY segments by window/step. Fully parameterized."
    )
    ap.add_argument("input", type=str, help="WAV file or folder with WAV files")
    ap.add_argument("--out", type=str, default="./out", help="Output directory")

    # Audio / STFT / mel
    ap.add_argument("--sr", type=int, default=44100)
    ap.add_argument("--n-fft", type=int, default=1024)
    ap.add_argument("--hop", type=int, default=256)
    ap.add_argument("--n-mels", type=int, default=64)
    ap.add_argument("--fmin", type=float, default=20.0)
    ap.add_argument("--fmax", type=float, default=16000.0)
    ap.add_argument("--no-center", action="store_true", help="Disable STFT centering (enabled by default)")
    ap.add_argument("--top-db", type=float, default=80.0, help="dB compression range for power_to_db")
    ap.add_argument("--mono-strategy", choices=["mean", "first"], default="mean")

    # Segmentation → NPY
    ap.add_argument("--win-seconds", type=float, default=1.0, help="Window length [s]")
    ap.add_argument("--step-seconds", type=float, default=0.5, help="Step between windows [s]")
    ap.add_argument("--pad-last", action="store_true", help="Pad the last window if incomplete")
    ap.add_argument("--pad-value", type=float, default=-80.0, help="dB value for padding the last window")
    ap.add_argument("--save-mode", choices=["stack", "separate"], default="stack")
    ap.add_argument("--dtype", choices=["float32", "float16"], default="float32")
    ap.add_argument("--save-full-mel", action="store_true", help="Also save full mel-log to NPY")

    # Visualization / index
    ap.add_argument("--png", action="store_true", help="Save mel-log PNG for the entire file")
    ap.add_argument("--save-individual-png", action="store_true", help="Save PNG for each NPY segment")
    ap.add_argument("--index-csv", type=str, default="index.csv", help="CSV file name with segment index (in --out directory)")
    return ap

def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)

    in_path = Path(args.input)
    out_dir = Path(args.out)

    wavs = collect_wavs(in_path)
    if not wavs:
        raise SystemExit(f"No WAV files found at: {in_path}")

    summary_rows = []
    for wav in tqdm(wavs, desc="Processing"):
        file_out = out_dir / wav.stem
        sr, total_frames, frames_win, frames_step, rows = process_file(wav, file_out, args)
        for source, npy_path, i, start, end, start_s, end_s in rows:
            summary_rows.append([
                source, npy_path, i, start, end, start_s, end_s,
                sr, args.n_fft, args.hop, args.n_mels, args.fmin, args.fmax,
                args.win_seconds, args.step_seconds
            ])

    write_index_csv(out_dir / args.index_csv, summary_rows, args)
    print(f"\nDone. Results in: {out_dir.resolve()}\n")

if __name__ == "__main__":
    main()
