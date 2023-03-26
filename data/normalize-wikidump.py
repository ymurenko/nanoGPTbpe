import os
import argparse

# expands all files in an extracted wikidump from their directry structure to a single directory
# also renames them so they're in consecutive order (e.g. 1, 2, 3, 4, 5, ...)

def rename_files(input_dir, output_dir):
    file_count = 0
    if not os.path.exists(output_dir):
        os.mkdir(os.path.join(output_dir))
    for directory in os.listdir(input_dir):
        if directory == output_dir:  # Skip the 'normalize_out' directory
            continue
        print(f"Moving and renaming files in {input_dir}/{directory}...")
        for filename in os.listdir(os.path.join(input_dir, directory)):
            filepath = os.path.join(input_dir, directory, filename)
            if os.path.isfile(filepath):
                new_filepath = os.path.join(output_dir, f"{file_count}")
                print(filepath, new_filepath)
                os.rename(filepath, new_filepath)
                file_count += 1
        print("Done.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("output_dir")
    args = parser.parse_args()
    print(f"Directory {args.input_dir}, containing:")
    dir = os.listdir(args.input_dir)
    for item in dir[:5]:
        print(item)
    print("...")
    option = input("Continue? [Y/n]: ")
    if(option == 'Y'):
        rename_files(args.input_dir, args.output_dir)
    else:
        exit()