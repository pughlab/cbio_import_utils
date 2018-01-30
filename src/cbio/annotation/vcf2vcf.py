import os
import argparse
from string import Template

def get_options():

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cwd", type=str, required=True,
                        help="working directory for qsub logs etc.")
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="input vcf directory name e.g strelka")
    parser.add_argument("-o", "--output", type=str, required=True,
                        help="output vcf directory name e.g. mutect")
    parser.add_argument("-f", "--fasta", type=str, required=False,
                        help="reference genome fasta file including path",
                        default='/mnt/work1/users/pughlab/references/VEP_fasta/83_GRCh38/homo_sapiens/Homo_sapiens.GRCh38.dna.primary_assembly.fa')
    parser.add_argument("--vcf_tumor_id", type=str, required=False,
                        help="vcf tumor id", default='TUMOR')
    parser.add_argument("--vcf_normal_id", type=str, required=False,
                        help="vcf normal id", default='NORMAL')
    parser.add_argument("-t", "--debug", action="store_true",
                        help="debug mode for testing")
    return parser.parse_args()

def main():
    args = get_options()
    if args.debug:
        print (args)

    s = Template('/mnt/work1/users/pughlab/tools/vcf2maf-1.6.14/vcf2vcf.pl \
    --input-vcf $input_file \
    --output-vcf $output_vcf \
    --ref-fasta $fasta \
    --vcf-tumor-id $vcf_tumor_id \
    --vcf-normal-id $vcf_normal_id')

    for subdir, dirs, files in os.walk(args.input):
        for file in files:
            if not file.endswith("vcf"): continue
            d = dict(input_file =os.path.join(args.input, file),
                     output_vcf=os.path.join(args.output, file),
                     fasta = args.fasta,
                     vcf_tumor_id = args.vcf_tumor_id,
                     vcf_normal_id = args.vcf_normal_id)
            cmd = s.substitute(d)
            if not args.debug:
                os.system(cmd)
            else:
                print (cmd)

if __name__ == "__main__":
    main()