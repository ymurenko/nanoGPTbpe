import argparse
import os
import pickle
import threading
import numpy as np
from bpemb import BPEmb
from concurrent.futures import ThreadPoolExecutor

import os

bpemb_en = BPEmb(lang="en", dim=300, vs=10000)
unique_tokens = set()

# separates out the "_" from tokens to get word boundaries
def process_word_boundries(encoded_data):
    with_word_boundries = []
    for word in encoded_data:
        if word.startswith('▁'):
            with_word_boundries.append(' ')
            with_word_boundries.append(word[1:])
        else:
            with_word_boundries.append(word)
    return with_word_boundries

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("output_dir")
    args = parser.parse_args()

    lock = threading.Lock()
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    print("Getting meta info...\n")
    sorted_dir = sorted(os.listdir(args.input_dir), key=lambda file: [int(os.path.basename(file).strip(".txt"))])

    # using bpemb to get all the unique tokens, with word boundaries
    def get_chars(filename):
        filepath = os.path.join(args.input_dir, filename)
        if os.path.isfile(filepath) and not filename.startswith(('meta', 'train', 'input', 'val', 'unique_tokens')):
            with open(filepath, 'r', encoding="utf-8") as f:
                encoded_data = bpemb_en.encode(f.read())
                with_word_boundries = process_word_boundries(encoded_data)
                lock.acquire()
                global unique_tokens
                unique_tokens.update(with_word_boundries)
                lock.release()
    
    with ThreadPoolExecutor() as executor:
        executor.map(get_chars, sorted_dir)
     
    unique_tokens = sorted(list(unique_tokens))

    # create a mapping from tokens to integers
    stoi = { token:i for i,token in enumerate(unique_tokens) } # decoder dict
    itos = { i:token for i,token in enumerate(unique_tokens) } # encoder dict
    def encode(s):
        return [stoi[t] for t in s] # encoder: take a string, output a list of integers
    def decode(l):
        return ''.join([itos[i] for i in l]) # decoder: take a list of integers, output a string
    total_vocab_size = len(unique_tokens)
    meta = {
    'vocab_size': total_vocab_size,
    'itos': itos,
    'stoi': stoi,
    }
    print(f"Total vocab size: {total_vocab_size}")
    with open(os.path.join(args.output_dir, f"meta.pkl"), 'wb') as meta_f:
        pickle.dump(meta, meta_f)
    print("Creating train and val files...\n")

    # create dirs for train and val
    train_dir = os.path.join(args.output_dir, "train")
    val_dir = os.path.join(args.output_dir, "val")
    if not os.path.exists(train_dir):
        os.mkdir(train_dir)
    if not os.path.exists(val_dir):
        os.mkdir(val_dir)
    
    # main file prep script
    def prepare_files(filename):
        filepath = os.path.join(args.input_dir, filename)
        base_name = os.path.splitext(filename)[0]
        if os.path.isfile(filepath) and not filename.startswith(('meta', 'train', 'input', 'val', 'unique_tokens')):
            with open(filepath, 'r', encoding="utf-8", errors="ignore") as f:
                encoded_data = bpemb_en.encode(f.read())
                with_word_boundries = process_word_boundries(encoded_data)
                # get all the unique tokens that occur in this text
                num_tokens = len(with_word_boundries)
                print(f"{os.path.basename(filename)}: {num_tokens:,} tokens")
                
                # create the train and test splits
                train_data = with_word_boundries[:int(num_tokens*0.9)]
                val_data = with_word_boundries[int(num_tokens*0.9):]

                # encode both to integers
                train_ids = encode(train_data)
                val_ids = encode(val_data)
                print(f"Encoding done! train: {len(train_ids):,}, val: {len(val_ids):,}")

                # export to bin files
                train_ids = np.array(train_ids, dtype=np.uint16)
                val_ids = np.array(val_ids, dtype=np.uint16)
                train_ids.tofile(os.path.join(train_dir, f"{base_name}.bin"))
                val_ids.tofile(os.path.join(val_dir, f"{base_name}.bin"))
    
    with ThreadPoolExecutor() as executor:
        executor.map(prepare_files, sorted_dir)

    print("Done!\n")
    exit()

