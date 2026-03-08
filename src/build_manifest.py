import argparse
import hashlib
import io
import json
import os
import tempfile
from pathlib import Path
import datasets
import soundfile as sf
from datasets import load_dataset


def build_manifest(lang, output_dir, audio_dir, split, max_samples=None):
    out_path = Path(output_dir) / lang / "clean.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    data = load_dataset("facebook/multilingual_librispeech",
                        lang,
                        streaming=True,
                        split=split)

    # get raw bytes to later collect MD5 and ensure .wav writting
    data = data.cast_column("audio", datasets.Audio(decode=False))

    tmp_fd, tmp_path = tempfile.mkstemp(dir=out_path.parent,
                                        suffix=".jsonl")

    with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
        for i, example in enumerate(data):
            if max_samples is not None and i >= max_samples:
                break
                                                                                                                                                                                
            audio = example["audio"]
            audio_bytes = audio["bytes"]

            md5 = hashlib.md5(audio_bytes).hexdigest()

            # decode and wav writting
            signal, sr = sf.read(io.BytesIO(audio_bytes))
            stem = Path(audio["path"]).stem
            wav_out = Path(audio_dir) / lang / f"{stem}.wav"
            wav_out.parent.mkdir(parents=True, exist_ok=True)
            sf.write(wav_out, signal, sr)

            record = {
                "utt_id":    f"{lang}_{stem}",
                "lang":      lang,
                "wav_path":  str(wav_out),
                "ref_text":  example["transcript"],
                "ref_phon":  None,
                "audio_md5": md5,
                "sr":        sr,
            }

            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    os.replace(tmp_path, out_path)
    print(f"Clean manifest written in {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang",        required=True)
    parser.add_argument("--output_dir",  default="data/manifests")
    parser.add_argument("--audio_dir",   default="data/raw")
    parser.add_argument("--split",       default="train")
    parser.add_argument("--max_samples", type=int, default=None)
    args = parser.parse_args()

    build_manifest(args.lang, args.output_dir, args.audio_dir, args.split, args.max_samples)
