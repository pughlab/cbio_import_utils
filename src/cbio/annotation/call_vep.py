import os
import argparse
from string import Template

def get_options():

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="input vcf directory")
    parser.add_argument("-o", "--output", type=str, required=True,
                        help="vep output directory")
    parser.add_argument("-s", "--script_dir", type=str, required=False,
                        help="directory to store qsub script ",
                        default='vep_script')
    parser.add_argument("-f", "--fasta", type=str, required=False,
                        help="reference genome fasta file including path",
                        default='/mnt/work1/users/pughlab/references/VEP_fasta/83_GRCh37/Homo_sapiens.GRCh37.75.dna.primary_assembly.fa')
    parser.add_argument("-c", "--cache", type=str, required=False,
                        help="reference genome cache directory",
                        default='/mnt/work1/users/pughlab/references/VEP_fasta/87_GRCh37')
    parser.add_argument("-v", "--vep", type=int, required=False,
                        help="VEP version e.g 87", default=87)
    parser.add_argument("-t", "--debug", action="store_true",
                        help="debug mode for testing")
    return parser.parse_args()


def create_script(sh_file, cmd, version):
    with open(sh_file, 'w') as of:
        of.write("#!/bin/bash\n")
        of.write("#$ -cwd\n")
        of.write("#$ -S /bin/bash\n")
        of.write("module load perl/5.18.1\n")
        of.write("module load vep/%s\n"%version)
        of.write(cmd)
    print(sh_file)
    os.system("chmod 755 %s" % sh_file)

def main():
    args = get_options()
    if args.debug:
        print (args)

    s = Template('variant_effect_predictor.pl \
    --merged  --offline  \
    --dir_cache  $cache_dir \
    --species homo_sapiens \
    --format vcf \
    --fasta  $fasta \
    --everything --force_overwrite  --vcf  \
    -i $infile \
    -o $outfile')

    for subdir, dirs, files in os.walk(args.input):
        for file in files:
            if not file.endswith('vcf'): continue
            input_file = os.path.join(args.input, file)
            out_file = os.path.join(args.output, file.replace('vcf', 'vep.vcf'))
            sh_file = os.path.join(args.output, args.script_dir, file.replace('vcf','sh'))

            d = dict(cache_dir=args.cache,
                     fasta=args.fasta,
                     infile=input_file,
                     outfile=out_file)
            cmd = s.substitute(d)
            if args.debug:
                print (cmd)
            create_script(sh_file, cmd, args.vep)

if __name__ == "__main__":
    main()