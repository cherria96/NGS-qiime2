# QIIME2 NGS Analysis Pipeline

This repository contains scripts and instructions for processing and analyzing next-generation sequencing (NGS) data using **QIIME2** with the SILVA 138_99 database.  
It includes preprocessing, denoising, taxonomy assignment, diversity analysis, and optional taxonomy organization.

---

## 📦 Requirements

- **conda** (Anaconda or Miniconda; tested on Anaconda 2022.10)
- **QIIME2** (tested on version `2023.2`)
- Python 3
- SILVA Database (`SILVA_DB_138_99`) (Download from [here](https://docs.qiime2.org/2024.10/data-resources/))
- Internet access for QIIME2 visualization (`https://view.qiime2.org/`)

---

## 🔹 1. Activate QIIME2 Environment

```bash
conda activate qiime2-2023.2
cd NGS_qiime2/qiime2/qiime2
python create_metadata.py
```
## 🔹 2. Prepare Input Data
Create a folder named `fastq` with the following structure:
```bash
fastq/
 ├── ARC/
 │    ├── ARC_*.fastq.gz  # ARC fastq files
 ├── BAC/
 │    ├── BAC_*.fastq.gz  # BAC fastq files
 ├── sample-metadata-arc.tsv
 ├── sample-metadata-bac.tsv
```
Metadata files (sample-metadata-arc.tsv, sample-metadata-bac.tsv)
* Must be tab-separated (.tsv)
* First column must be sampleid (pattern: CJU-0d-ARC if fastq file is CJU-0d-ARC_S65_L001_R1_001.fastq.gz)
* Additional columns (e.g., time, experiment) can be added
Example:
```tsv
sampleid         time   experiment
PBAT2-end-ARC    end    PBAT2
PBAT2-mid-ARC    mid    PBAT2
```
💡 If creating metadata manually is burdensome, run:
```bash
python create_metadata.py
```
## 🔹 3. Directory Structure Before Running
You should now have:
```bash
fastq/
qiime2/  # Provided folder
```
## 🔹 4. Run QIIME2 Command Script
Navigate to:
```bash
cd NGS_qiime2/qiime2
```
Run
```bash
./qiime2_cmd.sh
```
Inputs during execution:
1. Domain of sequences (BAC or ARC)

Outputs:
* Trimmed sequences
* Denoised & merged sequences
* Statistics (sequence length, feature frequency, etc.)

## 🔹 5. Check Sample Frequencies
Go to [QIIME2 View](https://view.qiime2.org/) and upload:
```bash
NGS_qiime2/result/dada2_table.qzv
```
* From Overview, get: frequency per sample (median frequency)
* From Interactive Sample Detail, get: minimum feature count
Example values:
```bash
ARC: fps = 19,108 ; min = 1
BAC: fps = 29,881 ; min = 170
```
## 🔹 6. Run QIIME2 Analysis Script
```bash
./qiime2_analysis.sh
```
Inputs:
1. Domain (BAC or ARC)
2. Frequency per sample (median frequency; no commas)
3. Sampling depth (minimum feature count)
4. Categorical column from metadata file (for weighted UniFrac distance matrix)

Outputs:
* SILVA taxonomy matched files
* Diversity analysis results
## 🔹 7. Taxonomy Organization (Optional)
If you want a read abundance file separated by taxonomic hierarchy:
1. Go to [QIIME2 View](https://view.qiime2.org/) -> upload `silva_16S_barplot.qzv`
   * Set Taxonomic Level = 7 -> download CSV
2. Go to [QIIME2 View](https://view.qiime2.org/) -> upload `silva_16S_taxonomy.qzv`
   * Download TSV
3. Run:
   ```bash
   python taxa_organizer.py
   ```
Inputs:
1. CSV file (from step 1)
2. Metadata file
3. TSV file (from step 2)
4. Output Excel filename (e.g., output.xlsx)

Output will be saved in:
```bash
../taxa-organized/
```
## 🔹 8. NGS taxanomy formatting (Optional)
If you want to change outputfile from procedure 7 to rank formats:
Run:
```bash
python taxa_organized_organizer.py
```
Inputs: 
1. CSV file (outputfile from procedure 7)
2. Metadata file
3. Output Excel filename (e.g., output.xlsx)

Output will be saved in:
```bash
../ngs-organized/
```
---
## 📚 Notes & Tips
**QIIME2 File Types**
* `.qza` → data file
* `.qzv` → visualization file (open at QIIME2 View)

**SILVA Database**
* Currently uses SILVA_DB_138_99
* If updated, retrain the Naïve Bayes classifier:
  ```bash
  ./qiime2_NBclf.sh
  ```
⚠️ This step is time- and memory-intensive.

**Initial Environment Setup**
For new systems:
```bash
./qiime2_setting.sh
```
(Requires conda installed.)



