from tkinter import filedialog
import os


EXCEL_IN = filedialog.askopenfilename(title = "Open taxa organized file")
METADATA = filedialog.askopenfilename(title = "Open metadata file .tsv")
if not os.path.exists('ngs-organized'):
    os.makedirs('ngs-organized')

EXCEL_OUT = 'ngs-organized/' + input("file name (add .xlsx): ")

RANK_COLOR_RGB = {
    "1": "black",
    "2": "#00B050",  # green
    "3": "#FFC000",  # yellow
    "4": "#C00000",  # red
    "5": "#7030A0",  # purple
}
TAXON_TOP_LABEL = {
    "P": "Phylum",
    "C": "Class",
    "O": "Order",
    "F": "Family",
    "G": "Genus",
    "S": "Species",
    # If your sheet names differ (e.g., include more text), we map by prefix later.
}

SITE_ORDER_BASE = [
    "BSSG",
    "BSNS",
    "BSIG",
    "BSIGa",
    "BSIGb",
    "BSOC",
    "BSES",
    "DGGW",
    "DGDS",
    "DGJY",
    "DGGB",
    "DGDC",
    "DGYS",
    "DGYSa",
    "DGYSb",
    "USOS",
    "USYY",
    "USYJ",
    "GSGA",
    "GCGD",
    "MGYS",
    "MGYSb",
    "MGYSa",
    "MGYSc",
    "ADAS",
    "ADPC",
    "YCGH",
    "YCDG",
    "UJGN",
    "CGSJ",
    "GHGH",
    "GHGHa",
    "GHGHb",
    "GHHM",
    "GHJY",
    "MYSN",
    "SCHG",
    "YSDM",
    "YSYS",
    "JJNG",
    "JJYS",
    "CWMS",
    "CWSS",
]
