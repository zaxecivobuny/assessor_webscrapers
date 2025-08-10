
def stitch_files(source_file_name, parts):
    output_file_name = source_file_name % 0
    stitched_result = ''
    for i in range(1, parts + 1):
        with open(source_file_name % i, 'r') as f:
            stitched_result += f.read()

    with open(output_file_name, 'w') as f:
        f.write(stitched_result)


def main():
    source_file_name = 'locator_output_data_part_%d.csv'
    stitch_files(source_file_name, 18)
    # section_size = 200
    # split_file(source_file_name, section_size)


if __name__ == '__main__':
    main()
