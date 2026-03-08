import json
import argparse
import os
import tempfile
from pathlib import Path
import soundfile as sf
import torch
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC


def predict_manifest(input_manifest, output_dir, lang):
    out_path = Path(output_dir) / lang / "manifests" / "predictions.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-lv-60-espeak-cv-ft")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-lv-60-espeak-cv-ft")
    model.eval()

    tmp_fd, tmp_path = tempfile.mkstemp(dir=out_path.parent, suffix=".jsonl")

    with open(input_manifest, encoding="utf-8") as m_in, \
         os.fdopen(tmp_fd, "w", encoding="utf-8") as m_out:

        for line in m_in:
            example = json.loads(line)
            print(f"Predicting on file {example["utt_id"]}..")
            
            signal, sr = sf.read(example["wav_path"])
            input_values = processor(signal, sampling_rate=sr, return_tensors="pt").input_values

            with torch.no_grad():
                logits = model(input_values).logits

            predicted_ids = torch.argmax(logits, dim=-1)
            phon_pred = processor.batch_decode(predicted_ids)[0]

            out_example = {
                **example,
                "phon_pred": phon_pred,
            }
            m_out.write(json.dumps(out_example, ensure_ascii=False) + "\n")

    os.replace(tmp_path, out_path)
    print(f"Predictions written: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang",           required=True)
    parser.add_argument("--input_manifest", required=True)
    parser.add_argument("--output_dir",     default="data")
    args = parser.parse_args()

    predict_manifest(args.input_manifest, args.output_dir, args.lang)
    # pixi run python predict.py --lang french --input_manifest data/french/manifests/clean.jsonl
