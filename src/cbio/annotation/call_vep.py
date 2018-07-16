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
                        default='/mnt/work1/users/pughlab/references/VEP_fasta/92_GRCh37')
    parser.add_argument("-g", "--gnomad", type=str, required=False,
                        help="Genome Aggregation Database (gnomAD) data",
                        default='/mnt/work1/users/pughlab/references/gnomad/gnomad_v2.0.2/Exome/gnomad.exomes.r2.0.2.sites.vcf.gz')
    parser.add_argument("-v", "--vep", type=int, required=False,
                        help="VEP version e.g 92", default=92)
    parser.add_argument("--forks", type=int, required=False,
                        help="number of forks", default=4)
    parser.add_argument("--offset", type=int, required=False,
                        help="offset for split large vcf file", default=1000)
    parser.add_argument("-t", "--split", action="store_true",
                        help="split large vcf into smaller files")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="debug mode print commands")
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

    s = Template('variant_effect_predictor.pl\
                --fork $forks\
                --species homo_sapiens\
                --offline\
                --everything\
                --shift_hgvs 1\
                --check_existing\
                --total_length\
                --allele_number\
                --no_escape\
                --xref_refseq\
                --buffer_size 256\
                --dir $cache_dir\
                --fasta $fasta\
                --input_file $infile\
                --force_overwrite\
                --custom $gnomad,gnomAD,vcf,exact,0,AF_POPMAX,AF_AFR,AF_AMR,AF_ASJ,AF_EAS,AF_FIN,AF_NFE,AF_OTH,AF_SAS\
                --vcf\
                --output_file $outfile')

    if args.split:
        split_large_vcfs(args.input, args.offset)

    for subdir, dirs, files in os.walk(args.input):
        for file in files:
            if file.endswith(".vep.vcf"): continue
            if file.endswith(".vcf"):
                print (file)
                input_file = os.path.join(args.input, file)
                out_file = os.path.join(args.output, file.replace('vcf', 'vep.vcf'))
                script_dir = os.path.join(args.output, args.script_dir)
                if not os.path.exists(script_dir):
                    try:
                        os.mkdir(script_dir,0755)
                    except OSError as e:
                        print ("Error:Script directory exists")

                sh_file = os.path.join(script_dir, file.replace('vcf','sh'))

                d = dict(cache_dir=args.cache,
                         fasta=args.fasta,
                         infile=input_file,
                         outfile=out_file,
                         forks=args.forks,
                         gnomad=args.gnomad)
                cmd = s.substitute(d)
                if args.debug:
                    print (cmd)

                create_script(sh_file, cmd, args.vep)

if __name__ == "__main__":
    main()