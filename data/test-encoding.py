import argparse
import os
import pickle
import numpy as np

# decodes a file encoded using bpe + custom ids
# if encoding was done correctly, should produce legible text

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("context_length")
    args = parser.parse_args()

    meta_pkl = os.path.join(args.input_dir, "meta.pkl")
    train_file = os.path.join(args.input_dir, "train", "1.bin")

    print(f"Loading meta from {meta_pkl}...")
    with open(meta_pkl, 'rb') as f:
        meta = pickle.load(f)
    itos = meta['itos']
    decode = lambda l: ''.join([itos[i] for i in l])
    decoded_data = []
    with open(train_file, 'r') as f:
        data = np.fromfile(f, dtype=np.uint16)
        decoded_data = decode(data[:int(args.context_length)])
        print("decoded data from {train_file}}")
        print(''.join(decoded_data))