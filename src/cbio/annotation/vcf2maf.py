import os
import stat
import argparse
from string import Template
import subprocess

def get_options():

    parser = argparse.ArgumentParser()
    parser.add_argument("--species", type=str, required=False,
                        help="Ensembl-friendly name of species (e.g. mus_musculus for mouse)", default="homo_sapiens")
    parser.add_argument("--vep_data", type=str, required=False,
                        help="VEP's base cache/plugin directory", default='/mnt/work1/users/pughlab/references/VEP_fasta/92_GRCh37')
    parser.add_argument("--vep_path", type=str, required=False,
                        help="Folder containing the vep script", default="/mnt/work1/software/vep/92")
    parser.add_argument("-f", "--fasta", type=str, required=False,
                        help="Reference FASTA file including path",
                        default="/mnt/work1/users/pughlab/references/VEP_fasta/83_GRCh37/Homo_sapiens.GRCh37.75.dna.primary_assembly.fa")
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="Path to input file in VCF format")
    parser.add_argument("-o", "--output", type=str, required=True,
                        help="Path to output MAF file")
    parser.add_argument("--ncbi_build", type=str,
                        help="NCBI genome build name e.g. GRCh37", default="GRCh37")
    parser.add_argument("--vcf_TUMOR", type=str, required=False,
                        help="Tumor sample ID used in VCF's genotype columns", default="TUMOR")
    parser.add_argument("--vcf_NORMAL", type=str, required=False,
                        help="Matched normal ID used in VCF's genotype columns", default="NORMAL")
    parser.add_argument("--maf_center", type=str, required=False,
                        help="Variant calling center to report in MAF", default="VarScan2")
    parser.add_argument("--filter_vcf", type=str, required=False,
                        help="A VCF for FILTER common_variant.",
                        default="/mnt/work1/users/pughlab/cBioportal_import/vep_plugin_dir/ExAC.r0.3.sites.minus_somatic.vcf.gz")
    parser.add_argument("--separator", type=str, required=False,
                        help="Delimiter to separate sample ID", default="--")
    parser.add_argument("-t", "--debug", action="store_true",
                        help="Debug mode for testing")
    return parser.parse_args()

def get_sampleIDs_from_filename(sample_name, separator):
    try:
        return sample_name.strip().split(separator)
    except:
        return None, None

def get_sampleIDs_from_header(vcf_file):
    try:
        p = subprocess.Popen(['grep', '##DCC=', vcf_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        parts = p.communicate()[0].split("\n")
        sample_id = parts[1].split("=")[2].replace(">", '')
        normal_id = parts[2].split("=")[2].replace(">", '')
        return sample_id, normal_id
    except:
        return None, None

def main():
    args = get_options()
    print(args)
    #run vcf2maf using the retain-info option to retain gnomAD AF_POPMAX allele frequencies
    s = Template('perl /mnt/work1/users/pughlab/tools/vcf2maf-1.6.16/vcf2maf.pl\
                    --species $species\
                    --ncbi-build $ncbi_build\
                    --input-vcf $input_vcf\
                    --output-maf $out_maf\
                    --maf-center $maf_center\
                    --tumor-id $tumor_id\
                    --normal-id $normal_id\
                    --vcf-tumor-id $vcf_TUMOR\
                    --vcf-normal-id $vcf_NORMAL\
                    --vep-path $vep_path\
                    --vep-data $vep_data\
                    --ref-fasta $fasta\
                    --filter-vcf $filter_vcf\
                    --buffer-size 265\
                    --max-filter-ac 10\
                    --retain-info gnomAD_AF_POPMAX,gnomAD_AF_AFR,gnomAD_AF_AMR,gnomAD_AF_ASJ,gnomAD_AF_EAS,gnomAD_AF_FIN,gnomAD_AF_NFE,gnomAD_AF_OTH,gnomAD_AF_SAS\
                    --min-hom-vaf 0.7')

    vep_dir = args.input
    ouput_dir = args.output
    for subdir, dirs, files in os.walk(vep_dir):
        for file in files:
            if file.endswith("vep.vcf"): continue
            if file.endswith("vcf"):
                maf_file = os.path.join(ouput_dir, "{}".format(file.replace('vcf','maf')))
                if os.path.exists(maf_file): continue
                vep_file = os.path.join(vep_dir, file)
                print (vep_file)
                sample_id, normal_id = get_sampleIDs_from_filename(file.split(".")[0], args.separator)
                if not normal_id:
                    sample_id, normal_id = get_sampleIDs_from_header(vep_file)
                if not normal_id: continue
                print ("sample ID: {}".format(sample_id))
                print ("matched normal ID: {}".format(normal_id))

                d = dict(
                         species=args.species,
                         ncbi_build=args.ncbi_build,
                         input_vcf = os.path.join(vep_dir, file.replace("vcf","vcf")),
                         out_maf = maf_file,
                         maf_center = args.maf_center,
                         vep_data=args.vep_data,
                         vep_path=args.vep_path,
                         fasta=args.fasta,
                         filter_vcf = args.filter_vcf,
                         vcf_TUMOR= sample_id if not args.vcf_TUMOR else args.vcf_TUMOR,
                         vcf_NORMAL=normal_id if not args.vcf_NORMAL else args.vcf_NORMAL,
                         tumor_id=sample_id,
                         normal_id=normal_id)
                cmd = s.substitute(d)
                print (cmd)
                script_dir = os.path.join(ouput_dir, "maf_script")
                if not os.path.exists(script_dir):
                    try:
                        os.mkdir(script_dir,0755)
                    except OSError as e:
                        print ("Error:Script directory exists")
                out_file = os.path.join(script_dir,"{}".format(file.replace('vep.vcf', 'sh')))
                with open(out_file, 'w') as of:
                    of.write("#!/bin/bash\n")
                    of.write("#$ -cwd\n")
                    of.write("#$ -S /bin/bash\n")
                    of.write("module load perl/5.18.1\n")
                    of.write("module load vep/92\n")
                    of.write("module load samtools/1.3.1\n")
                    of.write(cmd)
                print (out_file)
                os.chmod(out_file, stat.S_IRWXU)
if __name__ == "__main__":
    main()