[Pipeline manual]
1. activate qiime2 environment
command :  conda activate qiime2-2023.2

cd NGS_qiime2/qiime2/qiime2
python create_metadata.py

2. Create a folder name 'fastq'. Under this directory, create folders and files like below.

fastq
 ㄴARC (folder)
	ㄴARC fastq.gz (fastq files)
 ㄴBAC (folder)
	ㄴBAC fastq.gz (fastq files)
 ㄴsample-metadata-arc.tsv (Refer to [Metadata file] to create)
 ㄴsample-metadata-bac.tsv

3. You will see two folders overall 
1) fastq	2) qiime2 (provided)

4. Go to qiime2 directory (most inner one) cd NGS_qiime2/qiime2/qiime2

5. execute qiime2_cmd.sh
command : ./qiime2_cmd.sh
 - this returns trimmed sequences, denoised&merged sequences, some statistics (seq length, feature frequency ..etc) files
 - Input 1: which domain of sequences to get, chosen either from BAC or ARC (You'll know what this is abt after executing qiime2_cmd.sh)

6. Go to 'https://view.qiime2.org/'. From the output files from procedure 5 (look for NGS_qiime2/qiime2/result folder), put 'dada2_table.qzv' as the input file.
 - get the info of frequency per sample from 'Overview'
 - get the info of minimum frequency count from 'Interactive Sample Detail'

Arc: fps = 19,108; 1
Bac: fps = 29,881; 170

7. execute qiime2_analysis.sh
command : ./qiime2_analysis.sh
 - this returns silva taxonomy matched files, diversity analysis results.
 - Input 1: which domain to get 
 - Input 2: frequency per sample (from procedure 6) (see overview>>median frequency; no comma in number)
 - Input 3 (sampling depth): minimum feature count (from procedure 6) (see interactive sample details)
 - Input 4: any categorical column from metadata file you want to categorize data (used in weighted unifrac distance matrix)

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
[Metadata file : sample-metadata-arc.tsv, sample-metadata-bac5.tsv]
This is the information you want to provide for each sample. It can be anything such as 'experiment', 'elapsed days', 'substrate' .. etc.
Only thing required (mandatory) is the first column named with 'sampleid' and should contain the sample name. 
The sample name should be in this pattern :
For example, if the name of fastq file is 'CJU-0d-ARC_S65_L001_R1_001.fastq', 
the sampleid should be 'CJU-0d-ARC'
'S65' refers to barcode sequence, 'L001' to lane number, 'R1' to the direction of the read, '001' to the set number. 

After creating 'sampleid' column, you can add any columns but with the 'tab' separtaion as you can see from the file extension 'tsv'.
For example,
sampleid	time	experiment
PBAT2-end-ARC	end	PBAT2
PBAT2-mid-ARC	mid	PBAT2

If it is too burden for creating metadata file, run create-metadata.py.
command : python create_metadata.py
It will create arc, bac metadata files each but adding descriptions should be manually done. 
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
[taxanomy organizing]
When you want get read abundance file with separate hierarchy, use 'taxa_organizer.py'

1. Go to 'https://view.qiime2.org/'. Put 'silva_16S_barplot.qzv' as the input file.

2. Set the Taxonomic Level with Level 7 and download the CSV

3. Go to 'https://view.qiime2.org/'. Put 'silva_16S_taxonomy.qzv' as the input file. Download the TSV file.

4. run taxa_organizer.py
command : python taxa_organizer.py
 - Input 1: CSV file downloaded from procedure 2
 - Input 2: Metadata file
 - Input 3: TSV file downloaded from procedure 3
 - Input 4: "file name".xlsx
 
 Output file installs in ../taxa-organized folder
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
[Others (FYI)]
*About qiime files
In qiime, we get files with extension of either qza or qzv. qzv files are simply the visualization of qza files. 
In order to visualize qzv files, go to 'https://view.qiime2.org/' and drag the files there. 

*Silva database
The pipeline is currently using SILVA_DB_138_99. It can be updated and modified. Let everyone knows, if silva database had been or needed to be updated.
With new database, it should be re-trained with naiive-bayers classifier which can be done by executing qiime2_NBclf.sh.
This takes a lot of time and memory, so be prepared.

*Initial setting
Those who wants to create qiime2 environment on personal computer, you can run qiime2_setting.sh. 
However, before running qiime2_setting.sh, conda should be installed on your computer.
This computer uses 2022.10 version of anaconda.
