import os
import argparse

def get_options():

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_vcf", type=str, required=True,
                        help="path to input vcf files")
    parser.add_argument("-o", "--out_file", type=str, required=True,
                        help="output file name including path")

    return parser.parse_args()

def main():
    args = get_options()
    with open(args.out_file, 'w') as of:
        for subdir, dirs, files in os.walk(args.input_vcf):
            for file in files:
                if not file.endswith("gz"): continue
                vcf_file_name = file.strip().split("_")[0]
                merge_cmd = 'vcf-merge %s %s > %s.vcf' % (file, file, vcf_file_name)
                print(merge_cmd)
                of.write("%s;\n" % merge_cmd)

if __name__ == "__main__":
    main()