import argparse
from datasets import load_dataset

def build_manifest(lang):
    data = load_dataset("facebook/multilingual_librispeech", "french", split="test[:5]")
    print(data[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", required=True)
    args = parser.parse_args()
    
    build_manifest(args.lang, args.output)