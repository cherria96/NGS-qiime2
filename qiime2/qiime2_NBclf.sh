#!/bin/bash

#VARIABLES
ARC_FPRIMER=ATTAGATACCCSBGTAGTCC
ARC_RPRIMER=GCCATGCACCWCCTCT

BAC_FPRIMER=CCAGCAGCCGCGGTAATACG
BAC_RPRIMER=GACTACCAGGGTATCTAATCC

cd SILVA_DB_138_99
mkdir classifier
cd classifier

SILVA_DB=../silva-uniq-seqs.qza
SILVA_TAX=../silva-uniq-tax.qza

EXTRACT_ARC=silva-ARC-extract.qza
EXTRACT_DEREP_ARC=silva-ARC-uniq-extract.qza
CLF_ARC=silva-ARC-clf.qza
EXTRACT_BAC=silva-BAC-extract.qza
EXTRACT_DEREP_BAC=silva-BAC-uniq-extract.qza
CLF_BAC=silva-BAC-clf.qza

echo "extract reference read"

qiime feature-classifier extract-reads \
	--i-sequences $SILVA_DB \
	--p-f-primer $ARC_FPRIMER \
	--p-r-primer $ARC_RPRIMER \
	--o-reads $EXTRACT_ARC

qiime feature-classifier extract-reads \
	--i-sequences $SILVA_DB \
	--p-f-primer $BAC_FPRIMER \
	--p-r-primer $BAC_RPRIMER \
	--o-reads $EXTRACT_BAC

echo "complete extraction & start dereplicate"

qiime rescript dereplicate \
    	--i-sequences $EXTRACT_ARC \
    	--i-taxa $SILVA_TAX \
    	--p-rank-handles 'silva' \
    	--p-mode 'uniq' \
    	--o-dereplicated-sequences $EXTRACT_DEREP_ARC \
    	--o-dereplicated-taxa  $EXTRACT_DEREP_ARC

qiime rescript dereplicate \
    	--i-sequences $EXTRACT_BAC \
    	--i-taxa $SILVA_TAX \
    	--p-rank-handles 'silva' \
    	--p-mode 'uniq' \
    	--o-dereplicated-sequences $EXTRACT_DEREP_BAC \
    	--o-dereplicated-taxa  $EXTRACT_DEREP_BAC
    
echo "complete dereplicate & start classifier training"

qiime feature-classifier fit-classifier-naive-bayes \
	--i-reference-reads $EXTRACT_DEREP_ARC \
	--i-reference-taxonomy $SILVA_TAX \
	--o-classifier $CLF_ARC

qiime feature-classifier fit-classifier-naive-bayes \
	--i-reference-reads $EXTRACT_DEREP_BAC \
	--i-reference-taxonomy $SILVA_TAX \
	--o-classifier $CLF_BAC

echo "complete classifier training"

