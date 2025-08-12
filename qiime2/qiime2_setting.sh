
conda update conda
conda install wget

wget https://raw.githubusercontent.com/qiime2/environment-files/master/latest/staging/qiime2-latest-py38-linux-conda.yml
conda env create -n qiime2 --file qiime2-latest-py38-linux-conda.yml
rm qiime2-latest-py38-linux-conda.yml

conda activate qiime2

