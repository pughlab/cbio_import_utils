import os
import argparse

def get_options():

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="input vcf directory")
    parser.add_argument("-o", "--output", type=str, required=True,
                        help="output vcf directory")
    parser.add_argument("-b", "--bedfile", type=str, required=False,
                        help="target bed file including path",
                        default='/mnt/work1/users/pughlab/references/intervals/SureSelect_Human_All_Exon_V5+UTRs/headless.S04380110_Padded.bed')
    parser.add_argument("-t", "--debug", action="store_true",
                        help="debug mode for testing")
    return parser.parse_args()

def main():
    args = get_options()
    for subdir, dirs, files in os.walk(args.input):
        for file in files:
            cmd = "bedtools intersect -a %s/%s -b %s -header > %s/%s"%(args.input,file, args.bedfile, args.output, file)
            print (cmd)
            if not args.debug:
                os.system(cmd)

if __name__ == "__main__":
    main()
