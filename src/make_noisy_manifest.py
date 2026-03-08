from pathlib import Path
import tempfile
import json
from add_noise import add_noise_to_file
import hashlib
import os
import argparse


def make_noisy_manifest(lang, input_manifest, output_dir, audio_dir, snr_db, seed=42):
    out_path = Path(output_dir) / lang / f"noisy{snr_db}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_fd, tmp_path = tempfile.mkstemp(dir=out_path.parent,
                                        suffix=".jsonl")

    with open(input_manifest, encoding="utf-8") as clean_m, \
            os.fdopen(tmp_fd, "w", encoding="utf-8") as noisy_m:
        for line in clean_m:
            example = json.loads(line)

            stem = Path(example["wav_path"]).stem
            noisy_wav = Path(audio_dir) / lang / f"{stem}.wav"
            noisy_wav.parent.mkdir(parents=True, exist_ok=True)

            add_noise_to_file(input_wav=example["wav_path"],
                              output_wav=noisy_wav,
                              snr_db=snr_db,
                              seed=seed)

            with open(noisy_wav, "rb") as f:
                audio_md5 = hashlib.md5(f.read()).hexdigest()

            noisy_manifest = {
                **example,
                "wav_path": str(noisy_wav),
                "audio_md5": audio_md5,
                "snr_db": snr_db
            }
            noisy_m.write(json.dumps(noisy_manifest, ensure_ascii=False) + "\n")

    os.replace(tmp_path, out_path)
    print(f"Noisy manifest written in {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang",           required=True)
    parser.add_argument("--input_manifest", required=True)
    parser.add_argument("--output_dir",     default="data/manifests")
    parser.add_argument("--audio_dir",      default="data/noisy")
    parser.add_argument("--snr_db",         type=float, required=True)
    parser.add_argument("--seed",           type=int,   default=42)
    args = parser.parse_args()

    make_noisy_manifest(args.lang,
                        args.input_manifest,
                        args.output_dir,
                        args.audio_dir,
                        args.snr_db,
                        args.seed)
