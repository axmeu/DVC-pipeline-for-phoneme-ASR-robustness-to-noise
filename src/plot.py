import json
import matplotlib.pyplot as plt
from pathlib import Path
import argparse


def load_all_metrics(input_dir):
    all_series = {}  # {lang: [(snr, per), ...]}
    clean_per = {}   # {lang: per}

    for path in Path(input_dir).glob("*/metrics/results_*.jsonl"):
        with open(path, encoding="utf-8") as f:
            pers = []
            lang = None
            snr = None
            for line in f:
                record = json.loads(line)
                lang = record["lang"]
                snr = record["snr_db"]
                pers.append(record["per"])

        if lang is None:
            continue

        mean_per = sum(pers) / len(pers)

        if lang not in all_series:
            all_series[lang] = []

        if snr is None:
            clean_per[lang] = mean_per
        else:
            all_series[lang].append((snr, mean_per))

    for lang in all_series:
        all_series[lang].sort(key=lambda x: x[0])

    return all_series, clean_per


def plot_per_vs_snr(input_dir, output_plot):
    Path(output_plot).parent.mkdir(parents=True, exist_ok=True)

    all_series, clean_per = load_all_metrics(input_dir)

    fig, ax = plt.subplots(figsize=(8, 5))

    for lang, results in all_series.items():
        snrs = [r[0] for r in results]
        pers = [r[1] for r in results]
        line, = ax.plot(snrs, pers, marker="o", label=lang)

        if lang in clean_per:
            ax.axhline(y=clean_per[lang], linestyle=":", alpha=0.5,
                       color=line.get_color(), label=f"clean_{lang}")

    # Cross-lingual mean
    if len(all_series) > 1:
        all_snrs = sorted(set(snr for results in all_series.values() for snr, _ in results))
        mean_pers = []
        for snr in all_snrs:
            vals = [dict(results)[snr] for results in all_series.values()
                    if snr in dict(results)]
            if vals:
                mean_pers.append(sum(vals) / len(vals))
        ax.plot(all_snrs, mean_pers, marker="s", linestyle="--",
                linewidth=2, color="black", label="mean")

    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("PER")
    ax.set_title("Phoneme Error Rate vs Noise Level")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(output_plot, dpi=150)
    print(f"Plot saved: {output_plot}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir",   default="data")
    parser.add_argument("--output_plot", default="results/per_plot.png")
    args = parser.parse_args()

    plot_per_vs_snr(args.input_dir, args.output_plot)