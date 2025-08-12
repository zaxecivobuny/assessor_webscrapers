import re


def parse_dimension_string(s):
    if len(s) < 4:
        return 'blank'
    elif 'IRR' in s:
        return 'IRR'
    # case 1, two numbers
    elif re.search('^\s*\d{4}\s*/\s*-\s*\d{4}\s*/\s*$', s):
        n = re.findall('\d{4}', s)
        return int(n[0]) * int(n[1])
    # case 2, n / n - n
    elif re.search('^\s*\d{4}\s*/\s*\d{4}\s*-\s*\d{4}\s*/\s*$', s):
        n = re.findall('\d{4}', s)
        return ((int(n[0]) + int(n[1])) / 2) * int(n[2])
    # case 3, n-n/n
    elif re.search('^\s*\d{4}\s*/\s*-\s*\d{4}\s*/\s*\d{4}\s*$', s):
        n = re.findall('\d{4}', s)
        return int(n[0]) * ((int(n[1]) + int(n[2])) / 2)
    # case 4, n/n-n/n
    elif re.search('^\s*\d{4}\s*/\s*\d{4}\s*-\s*\d{4}\s*/\s*\d{4}\s*$', s):
        n = re.findall('\d{4}', s)
        return ((int(n[0]) + int(n[1])) / 2) * ((int(n[2]) + int(n[3])) / 2)
    else:
        return 'unknown case'


def main():
    delimiter = '|'
    # a = parse_dimension_string('')
    # print('a', a)
    # a = parse_dimension_string('0040 /IRR-  0140 / 0160')
    # print('a', a)
    # a = parse_dimension_string('0050 /      -  0135 /')
    # print('a', a)
    # a = parse_dimension_string('0070 / 0077 -  0110 /')
    # print('a', a)
    # a = parse_dimension_string('0120 / 0090 -  0113 / 0102')
    # print('a', a)
    with open('dimensions.txt', 'r') as input_file:
        with open('dim_output.txt', 'w') as output_file:
            for line in input_file:
                string = line.rstrip()
                result = parse_dimension_string(string)
                print(result)
                output_line = ''
                # output_line += string
                # output_line += delimiter
                output_line += str(result)
                output_line += '\n'
                output_file.write(output_line)
                # break

if __name__ == '__main__':
    main()
