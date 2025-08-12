#!/bin/sh

#DIRR
echo "Enter the domain (ARC/BAC) : "
read DOMAIN
echo "DOMAIN : $DOMAIN"

echo "Number of CPU : "
read CPU
echo "CPU : $CPU"

mkdir -v ../result
mkdir -v ../result/$DOMAIN
cd ../result/$DOMAIN

echo $PWD 
#VARIABLES
NGS_PATH=../../fastq/$DOMAIN
OUTPUT=demux_seqs.qza


VISUAL_TRIM=primer_trimmed.qzv
OUTPUT_TRIM=primer_trimed.qza

ARC_FPRIMER=ATTAGATACCCSBGTAGTCC
ARC_RPRIMER=GCCATGCACCWCCTCT
BAC_FPRIMER=CCAGCAGCCGCGGTAATACG
BAC_RPRIMER=GACTACCAGGGTATCTAATCC

DADA_OUT=dada2_table.qza
DADA_REPSEQ=dada2_rep_seqs.qza
DADA_STATS=dada2_stats.qza

#NEED METADATA.TSV
METADATA_ARC=../../fastq/sample-metadata-arc.tsv
METADATA_BAC=../../fastq/sample-metadata-bac.tsv

#IMPORT DATA
qiime tools import \
  --type 'SampleData[PairedEndSequencesWithQuality]' \
  --input-path $NGS_PATH \
  --input-format CasavaOneEightSingleLanePerSampleDirFmt \
  --output-path $OUTPUT

#Primer trimming
if [ $DOMAIN = "BAC" ];then
	echo "domain is bacteria"
	FPRIMER=$BAC_FPRIMER
	RPRIMER=$BAC_RPRIMER
	METADATA=$METADATA_BAC
else
	echo "domian is archaea"
	FPRIMER=$ARC_FPRIMER
	RPRIMER=$ARC_RPRIMER
	METADATA=$METADATA_ARC
fi

qiime cutadapt trim-paired \
	--i-demultiplexed-sequences $OUTPUT \
	--p-front-f $FPRIMER \
	--p-front-r $RPRIMER \
	--p-cores $CPU \
	--o-trimmed-sequences $OUTPUT_TRIM \

#Data Visualization
qiime demux summarize\
	--i-data $OUTPUT_TRIM\
	--o-visualization $VISUAL_TRIM

##http://view.qiime2.org --> to visualize $VISUAL

#Denoising with DADA2
qiime dada2 denoise-paired \
	--i-demultiplexed-seqs $OUTPUT_TRIM \
	--p-trunc-len-f 0 \
	--p-trunc-len-r 0 \
	--p-max-ee-f 2 \
	--p-max-ee-r 2 \
	--p-trunc-q 5 \
	--p-chimera-method none \
	--p-n-threads 0 \
	--o-table $DADA_OUT \
	--o-representative-sequences $DADA_REPSEQ \
	--o-denoising-stats $DADA_STATS

qiime feature-table summarize \
  --i-table $DADA_OUT \
  --o-visualization dada2_table.qzv \
  --m-sample-metadata-file $METADATA

qiime feature-table tabulate-seqs \
  --i-data $DADA_REPSEQ \
  --o-visualization dada2_rep_seqs.qzv

qiime metadata tabulate \
  --m-input-file $DADA_STATS \
  --o-visualization dada2_stats.qzv


