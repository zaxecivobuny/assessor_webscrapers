import os


def split_file(input_file, rows_per_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    num_files = (total_lines + rows_per_file - 1) // rows_per_file

    base_name = os.path.splitext(input_file)[0]

    for i in range(num_files):
        start = i * rows_per_file
        end = min(start + rows_per_file, total_lines)
        output_filename = f"{base_name}_part_{i+1}.txt"
        with open(output_filename, 'w', encoding='utf-8') as out_file:
            out_file.writelines(lines[start:end])
        print(f"Wrote rows {start + 1} to {end} to {output_filename}")

def my_split_file(file_name, section_size):
    with open(source_file_name, "rb") as f:
        num_lines = sum(1 for _ in f)
    print(num_lines)
    num_sections = (num_lines + section_size - 1) // section_size
    print(num_sections) 
    file_extension = source_file_name.split('.')
    print(file_extension)
    with open(source_file_name):
        for i in range(num_sections):
            file_name_parts = source_file_name.split('.')
            current_file_section_name = file_name_parts[0]
            current_file_section_name += '_section_'
            current_file_section_name += str(i)
            current_file_section_name += '.'
            current_file_section_name += file_name_parts[1]
            with open(current_file_section_name,'w'):
                pass


def main():
    source_file_name = 'data/locator_number_list.txt'
    section_size = 200
    split_file(source_file_name, section_size)


if __name__ == '__main__':
    main()