import sys
import argparse
from lxml import html, etree
from .parse import  parse, show

parser = argparse.ArgumentParser(usage="Manager project, can create git , sync , encrypt your repo")
parser.add_argument("parse", help="default to initialize a projet in current dir")
parser.add_argument("--json", default=False,action='store_true', help="default to initialize a projet in current dir")
parser.add_argument('infile', 
                        nargs='?', 
                        type=argparse.FileType('r'),
                        default=sys.stdin)


def main():
    args = parser.parse_args()
    if args.infile:
    	res = parse(args.infile.read(), args.parse)
    	if args.json:
    		show(res, tp='json')
    	else:
    		show(res)



if __name__ == "__main__":
    main()
