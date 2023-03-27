"""
Variation of nanoGPT's 'sample.py' that allows for a prompt to be specified.
"""
import os
import pickle
from contextlib import nullcontext
import torch
import tiktoken
from model import GPTConfig, GPT
from tokenizers import Tokenizer

# -----------------------------------------------------------------------------
init_from = 'resume' # either 'resume' (from an out_dir) or a gpt2 variant (e.g. 'gpt2-xl')
meta_pkl_path = './data/prepare-out/meta.pkl'
out_dir = 'bpe-simplewiki-out' # ignored if init_from is not 'resume'
start = input("Enter a prompt: ") # or "" or etc. Can also specify a file, use as: "FILE:prompt.txt"
num_samples = 4 # number of samples to draw
max_new_tokens = 500 # number of tokens generated in each sample
temperature = 0.8 # 1.0 = no change, < 1.0 = less random, > 1.0 = more random, in predictions
top_k = 200 # retain only the top_k most likely tokens, clamp others to have 0 probability
seed = 69
device = 'cuda' # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1', etc.
dtype = 'bfloat16' # 'float32' or 'bfloat16' or 'float16'
compile = False # use PyTorch 2.0 to compile the model to be faster
exec(open('configurator.py').read()) # overrides from command line or config file
# -----------------------------------------------------------------------------

torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
torch.backends.cuda.matmul.allow_tf32 = True # allow tf32 on matmul
torch.backends.cudnn.allow_tf32 = True # allow tf32 on cudnn
device_type = 'cuda' if 'cuda' in device else 'cpu' # for later use in torch.autocast
ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
ctx = nullcontext() if device_type == 'cpu' else torch.amp.autocast(device_type=device_type, dtype=ptdtype)

# model
if init_from == 'resume':
    # init from a model saved in a specific directory
    ckpt_path = os.path.join(out_dir, 'ckpt.pt')
    checkpoint = torch.load(ckpt_path, map_location=device)
    gptconf = GPTConfig(**checkpoint['model_args'])
    model = GPT(gptconf)
    state_dict = checkpoint['model']
    unwanted_prefix = '_orig_mod.'
    for k,v in list(state_dict.items()):
        if k.startswith(unwanted_prefix):
            state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
    model.load_state_dict(state_dict)
elif init_from.startswith('gpt2'):
    # init from a given GPT-2 model
    model = GPT.from_pretrained(init_from, dict(dropout=0.0))

model.eval()
model.to(device)
if compile:
    model = torch.compile(model) # requires PyTorch 2.0 (optional)

print(f"Loading meta from {meta_pkl_path}...")
with open(meta_pkl_path, 'rb') as f:
    meta = pickle.load(f)
tokenizer = Tokenizer.from_file(os.path.join('./data', meta['tokenizer']))

# encode the beginning of the prompt
start_ids = tokenizer.encode(start).ids
x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...])

# run generation
with torch.no_grad():
    with ctx:
        with open("sample.txt", 'w', encoding="utf-8", errors="ignore") as f_out:
            sample_text = ''
            for k in range(num_samples):
                y = model.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)
                model_out = y[0].tolist()
                decoded_and_joined = (''.join(tokenizer.decode(model_out))).replace(' ', '')
                remove_extra_spaces = decoded_and_joined.replace('▁', ' ')
                sample_text += f'\n\n---- SAMPLE {k} -----\n' + remove_extra_spaces
                print(remove_extra_spaces)
                print('\n-------------------\n')
            f_out.write(sample_text)