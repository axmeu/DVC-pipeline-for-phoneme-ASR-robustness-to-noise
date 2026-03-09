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
import subprocess
from convert_lang import convert_lang


def extract_phonemes(transcript, lang):
    conv_lang = convert_lang(lang)

    cmd_line = ["espeak-ng", "-v", conv_lang, "-q", "--ipa", "--sep"]
    # espeak with *lang* voice with no sound output and ipa convention

    raw = subprocess.run(cmd_line,
                         input=transcript,
                         capture_output=True,
                         text=True,
                         timeout=10).stdout.strip()

    phonemes = [p.strip()
                .replace("ˈ", "")
                .replace("ˌ", "")
                .replace("-", "")
                for p in raw.split()]
    phonemes = [p for p in phonemes if p]
    return " ".join(phonemes)


def build_manifest(lang, output_dir, split, max_samples=None):
    out_path = Path(output_dir) / lang / "manifests" / "clean.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    audio_dir = Path(output_dir) / lang / "raw"
    audio_dir.mkdir(parents=True, exist_ok=True)

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
            wav_out = audio_dir / f"{stem}.wav"
            sf.write(wav_out, signal, sr)

            transcript = example["transcript"]
            phonemes = extract_phonemes(transcript, lang)

            record = {
                "utt_id":    f"{lang}_{stem}",
                "lang":      lang,
                "wav_path":  str(wav_out),
                "ref_text":  transcript,
                "ref_phon":  phonemes,
                "audio_md5": md5,
                "sr":        sr,
                "snr_db":    None
            }

            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    os.replace(tmp_path, out_path)
    print(f"Clean manifest written in {output_dir}")
    os._exit(0)  # the terminal was blocked otherwise even if it all 
    # loaded and worked


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang",        required=True)
    parser.add_argument("--output_dir",  default="data")
    parser.add_argument("--split",       default="train")
    parser.add_argument("--max_samples", type=int, default=None)
    args = parser.parse_args()

    build_manifest(args.lang, args.output_dir, args.split, args.max_samples)
    # pixi run python src/build_manifest.py --lang french --max_samples 1
