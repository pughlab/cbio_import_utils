#/bin/bash
#$ -S /bin/bash
#$ -cwd

## pre_vcf2maf.sh (preps VEP vcfs for parsing)
## Author: Cindy Yang
## usage: sh pre_vcf2maf.sh /mnt/work1/users/pughlab/projects/AML_Duplex_Seq/Patient/Varscan/VEP /mnt/work1/users/pughlab/projects/AML_Duplex_Seq/Patient/Varscan/VEP/preVCF2MAF

input_dir=$1
output_dir=$2

mkdir $output_dir
mkdir $output_dir/sh_scripts

cd $input_dir

for file in $(ls | grep ".vep.vcf$"); do
	# Establish identifier for filename
    identifier=$(echo $file | awk '{ gsub(/.vep.vcf/, ""); print }')
    sh_script=$output_dir/sh_scripts/$identifier.sh

	# Set-up file and load modules
	echo -e "#!/bin/bash \n#$ -cwd \n" >> $sh_script
	echo -e "module load samtools/1.8\nmodule load tabix\nmodule load python/2.7\nmodule load vcftools/0.1.15\n\n" >> $sh_script

	# Zip files for tabix
	echo -e "bgzip $input_dir/$file" >> $sh_script
	echo -e "bgzip $input_dir/$identifier.vcf" >> $sh_script

	# Tabix indexes a TAB-deliminated genome position file and creates an index file
	echo -e "tabix -p vcf $input_dir/$file.gz" >> $sh_script
	echo -e "tabix -p vcf $input_dir/$identifier.vcf.gz" >> $sh_script

	# Remember to pass the right path to perl5:
	echo -e "export PERL5LIB=$PERL5LIB:/mnt/work1/software/vcftools/0.1.15/share/perl5" >> $sh_script

	# Generate dual columns for Varscan2 vcf and VEP vcf by merging files
	echo -e "vcf-merge $input_dir/$file.gz $input_dir/$file.gz > $output_dir/$identifier.merged.vep.vcf" >> $sh_script
	echo -e "vcf-merge $input_dir/$identifier.vcf.gz $input_dir/$identifier.vcf.gz > $output_dir/$identifier.merged.vcf" >> $sh_script

done
