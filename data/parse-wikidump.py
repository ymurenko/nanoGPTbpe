import argparse
import json
import os
import re
from concurrent.futures import ProcessPoolExecutor

parser = argparse.ArgumentParser()
parser.add_argument("input_dir")
parser.add_argument("output_dir")
args = parser.parse_args()

if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

def remove_asian_chars(text):
    # clean out all asian characters, since they will increase the vocab size too much
    pattern = r'[\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\u3100-\u312F\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\uFE30-\uFE4F\uFF00-\uFFEF]'
    no_asian_chars = re.sub(pattern, '', text)
    # need to also remove all the commas inside parenthesis after removing asian chars "(,"
    return re.sub(r'\(,', '(', no_asian_chars)

# parses the json from a wikidump file, and writes the text to a new file
def process_json_files(file):
    print(f"Processing file: {file}")
    input_file_path = os.path.join(args.input_dir, file)

    output_file_name = f"{file}.txt"
    output_file_path = os.path.join(args.output_dir, output_file_name)

    try:
        with open(input_file_path, "r", encoding="utf-8", errors="ignore") as input_file:
            with open(output_file_path, "wb") as output_file:
                for line in input_file:
                    data = json.loads(line)
                    new_text = ''
                    for char in data["text"]:
                        new_text += char
                    cleaned_text = remove_asian_chars(new_text)
                    output_file.write(cleaned_text.encode("utf-8"))
    except Exception as e:
        print(f"Error processing file {file}: {e}")


if __name__ == "__main__":
    with ProcessPoolExecutor() as executor:
        executor.map(process_json_files, os.listdir(args.input_dir))
