# A Short Guide to Variant Annotation
## Objective
To annotate variants detected in VCF format to an output of MAF format that is compatible with cBioportal upload standards.
## Software required:
## 1. [Variant Effect Predictor](http://useast.ensembl.org/info/docs/tools/vep/index.html)
#### What does it do? 
For each variant in the vcf file, it provides further annotation of the variant including ExAC, dbSNP, and others if provided. 
- Input: VCF format from variants detected by various callers (Mutect, Mutect2, Strelka, Varscan2). File names must end with ‘.vcf’ 
- Output: VCF format (suffix: ‘vep.vcf’) or a tab-separated format that is NOT compatible with cBioportal 

## 2.  [vcf2maf.pl](https://github.com/mskcc/vcf2maf)
### What does it do? 
It is a wrapper written in Perl facilitates variant annotation using VEP AND parsing the annotated ‘vep.vcf’ to a cBioportal compatible MAF format. 
- Input: VCF format from variants detected by various callers (Mutect, Mutect2, Strelka, Varscan2). File names must end with ‘.vcf’ 
- Output: MAF format that is compatible with cBioportal 

## If vcf2maf.pl is doing both annotation and parsing, why are we still running VEP?
For vcf2maf.pl to run VEP properly in our compute environment, many dependancies have to be set up in a specific way. 
This can be pretty tricky. As well, there are many customizable variables when calling VEP (see the VEP manual) that 
you will be able to specify if you run VEP separately and will not be able to do if running vcf2maf.pl without customized 
modifications to the script. 

### By running VEP separately, followed by vcf2maf.pl, we will only be using the PARSER component of vcf2maf.pl
If you choose to use vcf2maf.pl for the whole variant annotation process, please ensure all data dependancies, 
genome build and annotation caches are compatible with your input data.

## Simplified step by step guide

1. Use VEP to annotate your .vcf file of variant calls.
2. Set up your directory structure as indicated (NB: This is very important)
3. Use vcf2maf.pl to parse the .vep.vcf file to .maf format

## vcf2maf.py
For tumor only samples, duplicate the sample column before running VEP. Alternatively, you can duplicate 
both the Varscan2/Mutect vcf and VEP vcf afterwards using the script (duplicate_tumor_sample.sh)

## Directory Structure
- input_dir
```
|— filename.vcf 
|— filename.vep.vcf
```
## Important Points
- the name of the unannotated vcf file must match the VEP annotated file
- unannotated vcf file must be in the same directory as the VEP annotated file
- the input-vcf is always the path to the UNANNOTATED vcf file. The suffix is .vcf, not vep.vcf.
- if the unannotated vcf has sample names listed simply as “TUMOR” and “NORMAL”, you will have to specify : vcf-tumor-id TUMOR, vcf-normal-id NORMAL, within the vcf2maf command to ensure variant-allele frequencies are parsed properly.
- to parse a VCF with only 1 column (single sample), provide only the tumor-id.

[More info](https://github.com/mskcc/vcf2maf)
