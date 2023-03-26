import argparse
import json
import os
import re

# parses the json from a wikidump file, and writes the text to a new file

def remove_tags(text):
    tag_re = re.compile(r'<[^>]+>')
    return tag_re.sub('', text)

def process_json_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    count = 0
    for file in os.listdir(input_dir):
        print(f"Processing file: {file}")
        input_file_path = os.path.join(input_dir, file)

        output_file_name = f"{count}.txt"
        output_file_path = os.path.join(output_dir, output_file_name)

        try:
            with open(input_file_path, "r", encoding="utf-8", errors="ignore") as input_file:
                with open(output_file_path, "wb") as output_file:
                    for line in input_file:
                        data = json.loads(line)
                        new_text = ''
                        for char in data["text"]:
                            new_text += char
                        output_file.write(new_text.encode("utf-8"))
        except Exception as e:
            print(f"Error processing file {file}: {e}")
        count+=1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("output_dir")

    args = parser.parse_args()

    process_json_files(args.input_dir, args.output_dir)
