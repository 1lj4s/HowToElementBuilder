import os

output_file = 'saved_code.py'
source_dir = 'Code'  # укажи нужную папку

with open(output_file, 'w', encoding='utf-8') as outfile:
    for root, dirs, files in os.walk(source_dir):
        for fname in sorted(files):
            if fname.endswith('.py'):
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, source_dir)
                outfile.write(f'\n# ===== File: {rel_path} =====\n\n')
                with open(full_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    outfile.write('\n')
print(f'Склеено в {output_file}')

# tree /F