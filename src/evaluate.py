import argparse
import json
import os
import tempfile
from pathlib import Path
from jiwer import wer


def compute_per(ref_phon, phon_pred):
    return wer(ref_phon, phon_pred)


def evaluate_manifest(input_manifest, output_dir, lang):
    out_path = Path(output_dir) / lang / "metrics" / "results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    total_per = 0.0
    n = 0

    with open(input_manifest, encoding="utf-8") as m:
        for line in m:
            example = json.loads(line)
            per = compute_per(example["ref_phon"], example["phon_pred"])
            total_per += per
            n += 1

    mean_per = total_per / n if n > 0 else 0.0

    tmp_fd, tmp_path = tempfile.mkstemp(dir=out_path.parent, suffix=".json")

    with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
        json.dump({"lang": lang, "mean_per": mean_per, "n_utterances": n}, f, indent=2)

    os.replace(tmp_path, out_path)
    print(f"PER ({lang}): {mean_per:.3f}, n={n}")
    print(f"Metrics written: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang",           required=True)
    parser.add_argument("--input_manifest", required=True)
    parser.add_argument("--output_dir",     default="data")
    args = parser.parse_args()

    evaluate_manifest(args.input_manifest, args.output_dir, args.lang)
    '''
    pixi run python evaluate.py --lang french --input_manifest\
    data/french/manifests/predictions.jsonl
    '''
