import os
import argparse
from string import Template
import subprocess

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
    parser.add_argument("-p", "--slots", type=int, required=False,
                        help="number of slots", default=2)
    parser.add_argument("--offset", type=int, required=False,
                        help="offset for split large vcf file", default=1000)
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

def get_header(vcf_file):
    try:
        p = subprocess.Popen(['grep', '#', vcf_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return p.communicate()[0].strip().split("\n")
    except:
        return None

def chop_header(vcf_file):
    try:
        p = subprocess.Popen(['grep', '-vP', '#', vcf_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return p.communicate()[0].strip().split("\n")
    except:
        return None


def get_line_count(vcf_file):
    try:
        p = subprocess.Popen(['wc','-l',vcf_file], stdin = subprocess.PIPE, stdout=subprocess.PIPE)
        return p.communicate()[0].split()[0]
    except:
        return None

def create_vcf(vcf_file, lines):
    with open(vcf_file, 'w') as of:
        for line in lines:
            of.write("{}\n".format(line))

def split_large_vcfs(vcf_dir, offset):
    for subdir, dirs, files in os.walk(vcf_dir):
        for file in files:
            if not file.endswith('vcf'): continue
            input_file = os.path.join(vcf_dir, file)
            total_lines = get_line_count(input_file)
            if int(total_lines) > offset:
                header = get_header(input_file)
                lines = chop_header(input_file)

                for i in range(0, len(lines), offset):
                    new_vcf = "{0}_{1}.vcf".format(input_file.replace(".vcf", ""), i)
                    create_vcf(new_vcf, header + lines[i:i + offset])
            try:
                os.remove(input_file)
            except: continue

def main():
    args = get_options()
    if args.debug:
        print (args)

    s = Template('variant_effect_predictor.pl \
    --fork $slots \
    --merged  --offline  \
    --dir_cache  $cache_dir \
    --species homo_sapiens \
    --format vcf \
    --fasta  $fasta \
    --everything --force_overwrite  --vcf  \
    -i $infile \
    -o $outfile')

    split_large_vcfs(args.input, args.offset)

    for subdir, dirs, files in os.walk(args.input):
        for file in files:
            print (file)
            input_file = os.path.join(args.input, file)
            out_file = os.path.join(args.output, file.replace('vcf', 'vep.vcf'))
            sh_file = os.path.join(args.output, args.script_dir, file.replace('vcf','sh'))

            d = dict(cache_dir=args.cache,
                     fasta=args.fasta,
                     infile=input_file,
                     outfile=out_file,
                     slots=args.slots)
            cmd = s.substitute(d)
            if args.debug:
                print (cmd)
            create_script(sh_file, cmd, args.vep)

if __name__ == "__main__":
    main()