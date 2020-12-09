# Text cleaning

`clean.py` is the original cleaning code that I used when adding hamlet.txt to tinyshakespeare.txt.

`play.py` is the newer version, which includes stripping folger prefix in file and dir names and options to format the plays and concatenate them into one text file for training.

`sp.txt` and `sp-prefix.txt` are the output files. `sp-prefix.txt` was the one I eventually used.
They only contain the plays, not poems and sonnets. (See `shakespeare-works` folder).

`sp.txt` - texts in the files directly related Folger were stripped away, and add `<|endoftext|>` between each play.

`sp-prefix.txt` - in addition to `sp.txt`, removed ACT and SCENE headers and separators, and prefixed each play with a unique number.

# Model training

## Sites that helped

- https://colab.research.google.com/drive/1VLG8e7YSEwypxU-noRNhsv5dW4NfTGce#scrollTo=aeXshJM-Cuaf
- https://www.gwern.net/GPT-2
- http://education.abcom.com/using-gpt-2-to-write-like-shakespeare/
- https://medium.com/@stasinopoulos.dimitrios/a-beginners-guide-to-training-and-generating-text-using-gpt2-c2f2e1fbd10a
- https://docs.aitextgen.io/

## Things I tried but got tripped up

- Try to train Huggingface Transformer...
  - Didn't know how to properly make a dataset
  - Didn't know how to use top-k sampling in the Huggingface pipeline, with the pytorch model (Didin't try TF2 model)
    - So I got worse results than my first attempt with TF1 using gpt2-simple
- Convert TF1 model into PyTorch
  - No "constants" file in pytorch_model.bin (tch-rs couldn't load it)
- Convert TF1 to mmdn IR (and eventually PyTorch)
  - Didn't know the output node name
- Save original fine-tuned GPT-2 into Keras
  - https://github.com/CyberZHG/keras-gpt-2
  - Couldn't load in TFJS
- Trying to load from sonos/tract
  - Feature incomplete: "stateless evaluation not implemented"

## Tips

- Quickly check if a file is valid UTF-8

`iconv -f UTF-8 -t UTF-8 FILE > /dev/nul` (valid utf-8 if no error and/or return code is 0)

credit: https://superuser.com/questions/649834/is-there-a-linux-command-to-find-out-if-a-file-is-utf-8

- Diff two directories
  https://stackoverflow.com/questions/2019857/diff-files-present-in-two-different-directories

In short: `diff -ur dir1 dir2`

# What I did instead

Train model with aitextgen, and use a proper backend instead of trying to put everying into the browser.
