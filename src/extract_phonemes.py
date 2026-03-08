import subprocess

text = "ses vêtements devinrent tout brillants"
phonemes = subprocess.run(
    ["espeak-ng", "-v", "fr", "-q", "--ipa"],
    input=text,
    capture_output=True,
    text=True,
)
phonemes = phonemes.stdout.strip()

convert_to_espeak = {"french": "fr",
                     "german": "de",
                     "dutch": "nl",
                     "spanish": "es",
                     "italian": "it",
                     "portuguese": "pt",
                     "polish": "pl"}

print(phonemes)

