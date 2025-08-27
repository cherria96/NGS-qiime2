import pandas as pd
import numpy as np
from functions.ProcessSheet import process_sheet
from functions.config import EXCEL_IN, EXCEL_OUT, METADATA
from functions.PromptValues import get_user_sort_spec_from_metadata,compute_global_sample_order

def list_target_sheets(xf):
    """Sheets to process: those containing '(%)'."""
    return [s for s in xf.sheet_names if "rank(%)" in s]

def main():
    xf = pd.ExcelFile(EXCEL_IN)
    sheets = list_target_sheets(xf)
    meta_df = pd.read_csv(METADATA, sep="\t", dtype=str)
    
    # Prompt ONCE, build global order ONCE
    sort_spec = get_user_sort_spec_from_metadata(meta_df, sampleid_col="sampleid")
    global_order = compute_global_sample_order(meta_df, sort_spec, sampleid_col="sampleid")
    with pd.ExcelWriter(EXCEL_OUT, engine="xlsxwriter") as writer:
        for sheet in sheets:
            process_sheet(xf, sheet, writer, global_sample_order = global_order)

    print("DONE")
    print("Output Excel:", EXCEL_OUT)


if __name__ == "__main__":
    main()