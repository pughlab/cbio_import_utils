import os
import argparse
from string import Template

def get_options():

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--root", type=str,
                        help="root directory")
    parser.add_argument("-i", "--input", type=str,
                        help="input vcf directory name e.g mutect")
    parser.add_argument("-o", "--output", type=str,
                        help="vep output directory name e.g. VEP/output")
    parser.add_argument("-s", "--script", type=str,
                        help="directory to store qsub script e.g. VEP/scripts")
    parser.add_argument("-f", "--fasta", type=str,
                        help="reference genome fasta file including path")
    parser.add_argument("-c", "--cache", type=str,
                        help="reference genome cache directory")
    parser.add_argument("-v", "--vep", type=int,
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
    print (args)
    root_dir = args.root
    print (root_dir)
    print (args.vep)
    s = Template('variant_effect_predictor.pl --merged  --offline  \
    --dir_cache  $cache_dir \
    --species homo_sapiens --format vcf \
    --fasta  $fasta \
    --everything --force_overwrite  --vcf  \
    -i $infile \
    -o $outfile')

    for subdir, dirs, files in os.walk(os.path.join(root_dir, args.input)):
        for file in files:
            print (file)
            input_file = os.path.join(args.root, args.input, file)
            out_file = os.path.join(args.root, args.output, file.replace('vcf', 'vep.vcf'))
            sh_file = os.path.join(args.root, args.script, file.replace('vcf','sh'))

            d = dict(cache_dir=args.cache,
                     fasta=args.fasta,
                     infile=input_file,
                     outfile=out_file)
            cmd = s.substitute(d)
            print (cmd)
            create_script(sh_file, cmd, args.vep)

if __name__ == "__main__":
    main()