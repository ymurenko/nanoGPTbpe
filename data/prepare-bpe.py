import argparse
import os
import pickle
import numpy as np
import multiprocessing
from tokenizers import normalizers, Tokenizer, trainers, pre_tokenizers, models, decoders
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

parser = argparse.ArgumentParser()
parser.add_argument("input_dir")
parser.add_argument("output_dir")
parser.add_argument("vocab_size", type=int)
args = parser.parse_args()

if not os.path.exists(args.output_dir):
    os.mkdir(args.output_dir)
train_dir = os.path.join(args.output_dir, "train")
val_dir = os.path.join(args.output_dir, "val")
if not os.path.exists(train_dir):
    os.mkdir(train_dir)
if not os.path.exists(val_dir):
    os.mkdir(val_dir)

# run by each thread in thread pool
def encode_chunk(chunk):
    tokenizer = Tokenizer.from_file(os.path.join(args.output_dir, "tokenizer.json"))
    return tokenizer.encode(chunk).ids

# run by each process in process pool
def prepare_files(filename):
    filepath = os.path.join(args.input_dir, filename)
    base_name = os.path.splitext(filename)[0]
    encoded_data = list()
    if os.path.isfile(filepath) and not filename.startswith(('meta', 'train', 'input', 'val', 'unique_tokens')):
        with open(filepath, 'r', encoding="utf-8", errors="ignore") as f:
            chunks = []
            while True:
                chunk = f.read(4096)  # Adjust the buffer size if needed
                if not chunk:
                    break
                chunks.append(chunk)

            # distribute the encoding work across multiple threads
            with ThreadPoolExecutor() as executor:
                encoded_chunks = list(executor.map(encode_chunk, chunks))
            try:
                for enc in encoded_chunks:
                    encoded_data.extend(enc)

                num_tokens = len(encoded_data)
                print(f"{os.path.basename(filename)}: {num_tokens:,} tokens")
                    
                # create the train and test splits
                train_ids = encoded_data[:int(num_tokens*0.9)]
                val_ids = encoded_data[int(num_tokens*0.9):]
                print(f"Encoding {filepath}! train length: {len(train_ids):,}, val length: {len(val_ids):,}")

                # export to bin files
                train_ids = np.array(train_ids, dtype=np.uint16)
                val_ids = np.array(val_ids, dtype=np.uint16)
                train_ids.tofile(os.path.join(train_dir, f"{base_name}.bin"))
                val_ids.tofile(os.path.join(val_dir, f"{base_name}.bin"))
            except Exception as e:
                print(f"Error encoding {filepath}: {e}")
        
if __name__ == "__main__":
    print("Training tokenizer...\n")
    files = os.listdir(args.input_dir)
    files_with_dir = [os.path.join(args.input_dir, file) for file in files]
    files = files
    tokenizer = Tokenizer(models.BPE())
    # Normalize data by removing accents, and lowercasing all characters
    tokenizer.normalizer = normalizers.Sequence([normalizers.StripAccents(), normalizers.Lowercase()])
    # Encodes all whitespaces with special token “▁” (U+2581) at the start of each word
    # This makes it easier to reconstruct sentences
    tokenizer.pre_tokenizer = pre_tokenizers.Sequence([pre_tokenizers.Metaspace(), pre_tokenizers.Punctuation()])
    trainer = trainers.BpeTrainer(vocab_size=args.vocab_size, special_tokens=["<PAD>", "<UNK>", "<BOS>", "<EOS>"])
    tokenizer.train(files_with_dir, trainer=trainer)

    print("Saving metadata and trained tokenizer...\n")
    tokenizer.save(os.path.join(args.output_dir, "tokenizer.json"))
    meta = {
    'vocab_size': args.vocab_size,
    'tokenizer': os.path.join(args.output_dir, "tokenizer.json"),
    }
    print(f"Total vocab size: {args.vocab_size}")
    with open(os.path.join(args.output_dir, f"meta.pkl"), 'wb') as meta_f:
        pickle.dump(meta, meta_f)

    print("Encoding train and validation files...\n")
    # distribute preparation work across multiple processes
    # use all but one of available cores (to avoid lockup lol)
    max_processes = multiprocessing.cpu_count() - 1
    with ProcessPoolExecutor(max_processes) as executor:
        executor.map(prepare_files, files)

    # do a sample decoding to make sure everything is working
    sample_file = os.path.join(train_dir, "1.bin")
    print(f"Preparation complete! Decoded sample from {sample_file}: \n")
    with open(sample_file, 'r') as f:
        data = np.fromfile(f, dtype=np.uint16)
        decoded_and_joined = (''.join(tokenizer.decode(data[:32]))).replace(' ', '')
        remove_extra_spaces = decoded_and_joined.replace('▁', ' ')
        print(remove_extra_spaces)
    exit()