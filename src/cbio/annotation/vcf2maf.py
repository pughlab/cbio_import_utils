import os
import argparse
from string import Template
import subprocess

def get_options():

    parser = argparse.ArgumentParser()
    parser.add_argument("--vep_data", type=str, required=False,
                        help="reference genome cache data", default='/mnt/work1/users/pughlab/references/VEP_fasta/83_GRCh37')
    parser.add_argument("--vep_path", type=str, required=False,
                        help="path to VEP installation", default="/mnt/work1/software/vep/83")
    parser.add_argument("-f", "--fasta", type=str, required=False,
                        help="reference genome fasta file including path",
                        default="/mnt/work1/users/pughlab/references/VEP_fasta/83_GRCh37/Homo_sapiens.GRCh37.75.dna.primary_assembly.fa")
    parser.add_argument("-c", "--cwd", type=str, required=True,
                        help="working directory")
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="input vep file path")
    parser.add_argument("-o", "--output", type=str, required=True,
                        help="vep output directory")
    parser.add_argument("--ncbi_build", type=str,
                        help="NCBI genome build name e.g. GRCh37", default="GRCh37")
    parser.add_argument("--vcf_TUMOR", type=str, required=False,
                        help="vcf TUMOR sample column name", default="TUMOR")
    parser.add_argument("--vcf_NORMAL", type=str, required=False,
                        help="NCBI genome build name e.g. GRCh37", default="NORMAL")
    parser.add_argument("--maf_center", type=str, required=False,
                        help="variant tool center", default="mutect")
    parser.add_argument("--filter_vcf", type=str, required=False,
                        help="filter vcf file",
                        default="/mnt/work1/users/pughlab/cBioportal_import/vep_plugin_dir/ExAC.r0.3.sites.minus_somatic.vcf.gz")
    parser.add_argument("--separator", type=str, required=False,
                        help="charactor used to separate sample ID", default="__")
    parser.add_argument("-t", "--debug", action="store_true",
                        help="debug mode for testing")
    return parser.parse_args()

def get_sampleIDs_from_filename(sample_name, separator):
    try:
        return sample_name.strip().split(separator)
    except:
        return None, None

def get_sampleIDs_from_header(vcf_file):
    try:
        p = subprocess.Popen(['grep', '#CHROM', vcf_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        parts = p.communicate()[0].split("\t")
        normal_id = parts[-1].replace("\n", "")
        sample_id = parts[-2]
        print("sample ID: %s" % sample_id)
        print("matched normal ID: %s" % normal_id)
        return sample_id, normal_id
    except:
        return None, None

def main():
    args = get_options()
    print(args)

    s = Template('perl /mnt/work1/users/pughlab/cBioportal_import/import_wrapper/scripts/v1.6.12/vcf2maf-1.6.12/vcf2maf.pl \
    --vep-data $vep_data \
    --vep-path $vep_path \
    --ref-fasta $fasta \
    --tmp-dir $tmp_dir \
    --ncbi-build $ncbi_build \
    --vcf-tumor-id $vcf_TUMOR \
    --vcf-normal-id  $vcf_NORMAL \
    --tumor-id $sample_id \
    --normal-id $normal_id \
    --input-vcf $input_vcf \
    --maf-center $maf_center \
    --filter-vcf /mnt/work1/users/pughlab/cBioportal_import/vep_plugin_dir/ExAC.r0.3.sites.minus_somatic.vcf.gz \
    --output-maf $maf')

    vep_dir = args.input
    tmp_dir = args.cwd
    ouput_dir = args.output
    for subdir, dirs, files in os.walk(vep_dir):
        for file in files:
            if file.endswith("vep.vcf"):
                maf_file = os.path.join(ouput_dir, "{}".format(file.replace('vep.vcf','maf')))
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
                        vep_data=args.vep_data,
                        vep_path=args.vep_path,
                        fasta=args.fasta,
                        ncbi_build=args.ncbi_build,
                        tmp_dir=tmp_dir,
                        vcf_TUMOR=args.vcf_TUMOR,
                        vcf_NORMAL=args.vcf_NORMAL,
                        sample_id=sample_id,
                        normal_id=normal_id,
                        input_vcf=os.path.join(vep_dir, file),
                        maf_center=args.maf_center,
                        maf=maf_file)
                cmd = s.substitute(d)
                print (cmd)
                out_file = os.path.join(ouput_dir,"maf_script","{}.sh".format(file.replace('vep.vcf', 'sh')))
                with open(out_file, 'w') as of:
                    of.write("#!/bin/bash\n")
                    of.write("#$ -cwd\n")
                    of.write("#$ -S /bin/bash\n")
                    of.write("module load perl/5.18.1\n")
                    of.write("module load vep/83\n")
                    of.write("module load samtools/1.3.1\n")
                    of.write(cmd)
                print (out_file)
                os.system("chmod 755 %s"%out_file)

if __name__ == "__main__":
    main()