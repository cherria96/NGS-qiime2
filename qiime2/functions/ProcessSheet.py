import pandas as pd
import numpy as np
from functions.config import EXCEL_IN, METADATA, TAXON_TOP_LABEL
from functions.ProcessHelper import build_site_header_row,find_read_sheet_name,\
    append_total_reads_row,\
        compute_minor_unidentified_identified_total,append_summary_rows,\
    compute_ranking_blocks,append_ranking_rows,write_sheet_with_formatting
from functions.PromptValues import apply_global_sample_order_to_df

def read_sheets(xf: pd.ExcelFile, sheet: str) -> pd.DataFrame:
    return xf.parse(sheet)

def process_sheet(xf: pd.ExcelFile, sheet: str, writer: pd.ExcelWriter, global_sample_order) -> None:
    """Full pipeline for one sheet."""
    df = read_sheets(xf, sheet)
    tax_col = df.columns[0]
    sample_cols = list(df.columns[1:])
    meta_df = pd.read_csv(METADATA, sep="\t", dtype=str)

    # Insert description row (1st row as the column names)
    df = build_site_header_row(df, meta_df, sampleid_col="sampleid")

    # Append Total reads row from *_read sheet
    read_sheet = find_read_sheet_name(sheet)
    read_df = pd.read_excel(EXCEL_IN, sheet_name=read_sheet, engine="openpyxl")
    df = append_total_reads_row(df, read_df)
    
    # sort samples based on prompted priority
    df = apply_global_sample_order_to_df(df, global_sample_order)
    
    # Compute summary rows then append them
    minor_group, unidentified_vals, identified_vals, total_vals = compute_minor_unidentified_identified_total(df)
    df_out = append_summary_rows(df, minor_group, unidentified_vals, identified_vals, total_vals)

    # Ranking blocks
    row_colors, rows_values, row_sum_1_3, row_sum_1_5, rows_taxa, top_taxa_by_rank = compute_ranking_blocks(df_out)
    df_out = append_ranking_rows(df_out, row_colors, rows_values, row_sum_1_3, row_sum_1_5, rows_taxa)

    # Write with formatting & coloring
    prefix = sheet.split("_", 1)[0]
    top_label = TAXON_TOP_LABEL.get(prefix, "")
    write_sheet_with_formatting(writer, sheet, df_out, top_label, top_taxa_by_rank)