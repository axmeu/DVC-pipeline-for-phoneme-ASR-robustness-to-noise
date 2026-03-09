import argparse
import json
import os
import tempfile
from pathlib import Path
from jiwer import wer


def evaluate_manifest(input_manifest, output_dir, lang, snr_db):
    noise_level = f"snr{int(snr_db)}" if snr_db is not None else "clean"
    out_path = Path(output_dir) / lang / "metrics" / f"results_{noise_level}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_fd, tmp_path = tempfile.mkstemp(dir=out_path.parent, suffix=".jsonl")

    with open(input_manifest, encoding="utf-8") as m_in, \
         os.fdopen(tmp_fd, "w", encoding="utf-8") as m_out:
        for line in m_in:
            example = json.loads(line)
            per = wer(example["ref_phon"], example["phon_pred"])
            record = {
                **example,
                "per": per
            }
            m_out.write(json.dumps(record, ensure_ascii=False) + "\n")

    os.replace(tmp_path, out_path)
    print(f"Metrics written: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang",           required=True)
    parser.add_argument("--input_manifest", required=True)
    parser.add_argument("--output_dir",     default="data")
    parser.add_argument("--snr_db",         type=float, default=None)
    args = parser.parse_args()

    evaluate_manifest(args.input_manifest, args.output_dir, args.lang, args.snr_db)
    '''
    pixi run python src/evaluate.py --lang french --input_manifest\
    data/french/manifests/predictions_clean.jsonl
    '''
