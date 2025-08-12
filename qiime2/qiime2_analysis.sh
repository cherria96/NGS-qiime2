#!/bin/bash

CLF_ARC=../../qiime2/silva_16S_ARC_classifier.qza
CLF_BAC=../../qiime2/silva_16S_BAC_classifier.qza
SEQ=dada2_rep_seqs.qza
TABLE=dada2_table.qza
METADATA_ARC=../../fastq/sample-metadata-arc.tsv
METADATA_BAC=../../fastq/sample-metadata-bac.tsv

TAXA=silva_16S_taxonomy.qza
SEQ_FILT=seq_filtered.qza
TABLE_FILT=table_filtered.qza
TREE=rooted-tree.qza
METRIC_DIRR=core-metrics-results

echo "Enter the domain (ARC/BAC): "
read DOMAIN
echo "DOMAIN : $DOMAIN"

if [ $DOMAIN = "ARC" ];then
	echo "domain is archaea"
	CLF=$CLF_ARC
	cd ../result/ARC
	METADATA=$METADATA_ARC
	FILTER=Bacteria
else
	echo "domain is bacteria"
	CLF=$CLF_BAC
	cd ../result/BAC
	METADATA=$METADATA_BAC
	FILTER=Archaea
fi
echo "$CLF"

echo "start classification"

qiime feature-classifier classify-sklearn \
	--i-classifier $CLF \
	--i-reads $SEQ \
	--o-classification $TAXA

echo "complete classificatin"

echo "filtration"
echo "filtered domain : $FILTER"

qiime taxa filter-seqs \
	--i-sequences $SEQ \
       	--i-taxonomy $TAXA \
       	--p-exclude $FILTER \
       	--o-filtered-sequences $SEQ_FILT

qiime taxa filter-table \
	--i-table $TABLE \
       	--i-taxonomy $TAXA \
       	--p-exclude $FILTER \
       	--o-filtered-table $TABLE_FILT

qiime metadata tabulate \
	--m-input-file $TAXA \
	--o-visualization silva_16S_taxonomy.qzv

qiime taxa barplot \
	--i-table $TABLE_FILT \
	--i-taxonomy $TAXA \
	--m-metadata-file $METADATA \
	--o-visualization silva_16S_barplot.qzv

qiime phylogeny align-to-tree-mafft-fasttree \
	--i-sequences $SEQ_FILT \
	--o-alignment aligned-rep-seqs.qza \
	--o-masked-alignment masked-aligned-rep-seqs.qza \
	--o-tree unrooted-tree.qza \
	--o-rooted-tree $TREE

#--p-max-depth : median frequency value of frequency per sample from dada_table.qzv
echo "start diversity analysis"
echo "Median frequency value of frequency per sample : "
read FREQ
echo "Frequency : $FREQ"

qiime diversity alpha-rarefaction \
	--i-table $TABLE_FILT \
	--i-phylogeny $TREE \
	--p-max-depth $FREQ \
	--m-metadata-file $metadata \
	--o-visualization alpha_rarefaction.qzv

#--p-sampling-depth : total frequency that each sample should be rarefied (output from alpha diversity analysis)

echo "sampling depth for diversity analysis:"
read DEPTH
echo "sampling depth : $DEPTH"


qiime diversity core-metrics-phylogenetic \
	--i-phylogeny $TREE \
	--i-table $TABLE_FILT \
	--p-sampling-depth $DEPTH \
	--m-metadata-file $METADATA \
	--output-dir $METRIC_DIRR

echo "metadata column for beta diversity column (categorical) : "
read CAT_COLUMN
echo "Column : $CAT_COLUMN"

qiime diversity beta-group-significance \
	--i-distance-matrix $METRIC_DIRR/weighted_unifrac_distance_matrix.qza \
	--m-metadata-file $METADATA \
	--m-metadata-column $CAT_COLUMN \
	--o-visualization $METRIC_DIRR/weighted-unifrac-body-site-significance.qzv \
	--p-pairwise

qiime diversity alpha-group-significance \
	--i-alpha-diversity $METRIC_DIRR/faith_pd_vector.qza \
	--m-metadata-file $METADATA \
	--o-visualization $METRIC_DIRR/faith_pd-group-significance.qzv

qiime diversity alpha-group-significance \
	--i-alpha-diversity $METRIC_DIRR/evenness_vector.qza \
	--m-metadata-file $METADATA \
	--o-visualization $METRIC_DIRR/evenness-group-significance.qzv

qiime emperor plot \
	--i-pcoa $METRIC_DIRR/unweighted_unifrac_pcoa_results.qza \
	--m-metadata-file $METADATA \
	--o-visualization $METRIC_DIRR/unweighted_unifrac_PCoA.qzv

qiime emperor plot \
	--i-pcoa $METRIC_DIRR/bray_curtis_pcoa_results.qza \
	--m-metadata-file $METADATA \
	--o-visualization $METRIC_DIRR/bray-curtis_PCoA.qzv

echo "complete diversity analysis"

