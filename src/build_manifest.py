import argparse
from datasets import load_dataset
import datasets

def build_manifest(lang):
    data = load_dataset("facebook/multilingual_librispeech", 
                        lang,
                        streaming=True,
                        split="train")

    data = data.cast_column("audio", datasets.Audio(decode=False))
    example = next(iter(data.take(1)))
    print(example.keys())

    print(example["original_path"])
    # http://www.archive.org/download/evangilestmarc-lemaistredesacy_1507_librivox/evangilestmarc_09_lemaistredesacy_64kb.mp3

    """
    utt_id : original_path (to cut)
    — lang : lang arg 
    — wav_path : relative path to the audio file. TO FIND
    — ref_text : transcript with espeak-ng
    — ref_phon : NEXT STEP
    — audio_md5 : checksum to ensure traceability 
    - durations: end_time - begin_time
    - ref_phon: NEXT STEP 
    - sr: ??
    """
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", required=True)
    args = parser.parse_args()

    build_manifest(args.lang)