#!/usr/bin/python3

def main(args):
    if args.listMultiple:
        print('listMultiple: 1, 2, 3, 4, 5')

    if args.index:
        print('index: ', args.index)

    print('test')
    return



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='a script that is meant to demonstrate CLI functionality')
    observationsAmount = parser.add_mutually_exclusive_group()
    observationsAmount.add_argument('--listMultiple', required=False, action='store_true', help='Whether or not to show all args')
    observationsAmount.add_argument('--index', metavar='###', required=False, help='Does absolutely nothing')

    args = parser.parse_args()
    main(args)