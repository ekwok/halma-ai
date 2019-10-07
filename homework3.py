def main():
    with open('input.txt') as infile:
        TYPE = infile.readline().strip()
        COLOR = infile.readline().strip()
        TIME = float(infile.readline().strip())
        BOARD = [['.'] * 16] * 16


if __name__ == '__main__':
    main()
