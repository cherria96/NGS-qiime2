import pandas as pd
from functions.config import RANK_COLOR_RGB
import numpy as np

def build_site_header_row(
    df: pd.DataFrame,
    meta_df: pd.DataFrame,
    sampleid_col: str = "sampleid",
) -> pd.DataFrame:
    """
    Insert description rows from metadata at the top of df.

    - Assumes the FIRST ROW of df (row 0) holds sample IDs for columns 1..N.
    - meta_df must have a `sampleid_col` column plus any number of
      description columns (e.g., site, round, batch, etc.).
    - For each description column in meta_df (excluding `sampleid_col`),
      we append one row labeled with that column name in the taxonomy/label column,
      and values per sample column aligned by sample ID.

    Parameters
    ----------
    df : DataFrame
        Input table where df.iloc[0, 1:] are sample IDs.
        Column 0 is the taxonomy/label column.
    meta_df : DataFrame
        Metadata with at least [sampleid_col, <desc1>, <desc2>, ...].
    sampleid_col : str
        Name of the sample id column in metadata.
    Returns
    -------
    DataFrame with the description rows inserted.
    """
    df = df.copy()

    # Basic checks and normalization
    if sampleid_col not in meta_df.columns:
        raise ValueError(f"Metadata is missing required column '{sampleid_col}'.")

    # Ensure string types for safe mapping
    meta_df = meta_df.copy().astype(str)
    # If duplicate sampleids exist, keep the first occurrence
    meta_df = meta_df.drop_duplicates(subset=[sampleid_col], keep="first")

    # Columns
    tax_col = df.columns[0]
    sample_cols = list(df.columns[1:])

    # The first row of df contains sample IDs for each sample column
    sample_ids = meta_df.iloc[0, 1:].astype(str).tolist()

    # Description columns come from metadata, excluding the sampleid column
    desc_cols = [c for c in meta_df.columns if c != sampleid_col]

    # Build a mapping {desc_col: {sampleid -> value}}
    desc_maps = {c: dict(zip(meta_df[sampleid_col], meta_df[c])) for c in desc_cols}

    # Build description rows
    desc_rows = []
    for desc in desc_cols:
        row_dict = {tax_col: desc}
        m = desc_maps[desc]
        for col in sample_cols:
            row_dict[col] = m.get(col, "")  # empty if missing in metadata
        desc_rows.append(row_dict)

    desc_df = pd.DataFrame(desc_rows, columns=df.columns) if desc_rows else pd.DataFrame(columns=df.columns)

    out = pd.concat([desc_df, df], ignore_index=True)
    return out

def find_read_sheet_name(sheet_name: str) -> str:
    """
    From '(%)' sheet, infer its *_read sheet name.
    E.g., 'P(%)' -> 'P_read'
    """
    prefix = sheet_name.split("_", 1)[0]
    return f"{prefix}_read"

def append_total_reads_row(df: pd.DataFrame, read_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-sample total reads from the *_read sheet and append a 'Total reads' row.
    Assumes first column is taxonomy column; samples are the rest.
    """
    tax_col = df.columns[0]
    sample_cols = list(df.columns[1:])
    common = [c for c in sample_cols if c in read_df.columns]
    read_sums = read_df[common].sum(axis=0, numeric_only=True)

    total_reads_row = pd.Series(0, index=sample_cols, dtype="float64")
    total_reads_row.loc[common] = read_sums
    total_reads_df = pd.DataFrame([{tax_col: "Total reads", **total_reads_row.to_dict()}])

    return pd.concat([df, total_reads_df], ignore_index=True)

            
def compute_minor_unidentified_identified_total(df):
    """
    Returns (minor_group, unidentified_vals, identified_vals, total_vals).
    Minor = 100 - sum(columns) over rows [2 : -1] (i.e., excluding the 'Total reads' row just appended).
    Clip negatives to 0.
    """
    tax_col = df.columns[0]
    sample_cols = list(df.columns[1:])

    # Minor group
    col_sums = df[sample_cols].iloc[2:-1].sum(axis=0)
    minor_group = (100 - col_sums).clip(lower=0)

    # Unidentified
    mask_unid = df[tax_col].astype(str).str.contains("unidentified", case=False, na=False)
    if mask_unid.any():
        unidentified_vals = df.loc[mask_unid, sample_cols].iloc[0]
        df.drop(df.index[mask_unid], inplace=True)
    else:
        unidentified_vals = pd.Series([0] * len(sample_cols), index=sample_cols)

    # Identified
    identified_vals = 100 - unidentified_vals

    # Total reads (extract then remove)
    mask_total = df[tax_col].astype(str).str.contains("Total reads", case=False, na=False)
    if mask_total.any():
        total_vals = df.loc[mask_total, sample_cols].iloc[0]
        df.drop(df.index[mask_total], inplace=True)
    else:
        total_vals = pd.Series([0] * len(sample_cols), index=sample_cols)

    return minor_group, unidentified_vals, identified_vals, total_vals

def append_summary_rows(df: pd.DataFrame,
                        minor_group: pd.Series,
                        unidentified_vals: pd.Series,
                        identified_vals: pd.Series,
                        total_vals: pd.Series) -> pd.DataFrame:
    """Append the 4 summary rows to df (minor group, unidentified, Identified, Total reads)."""
    tax_col = df.columns[0]
    sample_cols = list(df.columns[1:])
    extra_rows = pd.DataFrame({tax_col: ["minor group (<1%)", "unidentified", "Identified", "Total reads"]})
    extra_rows = pd.concat(
        [
            extra_rows,
            pd.DataFrame(
                [minor_group.values, unidentified_vals.values, identified_vals.values, total_vals.values],
                columns=sample_cols,
            ),
        ],
        axis=1,
    )
    return pd.concat([df, extra_rows], ignore_index=True)

def compute_ranking_blocks(df_out, k: int = 5):
    """
    Build the ranking blocks from rows above 'minor group (<1%)'.
    Returns:
      row_colors          (# of colors)
      rows_values         (rank values rows '1'..'k')
      row_sum_1_3 / _1_5  (sum rows)
      rows_taxa           (taxon name rows '1'..'k')
    """
    tax_col = df_out.columns[0]
    sample_cols = list(df_out.columns[1:])

    # cutoff (row index for "minor group (<1%)")
    minor_idx_list = df_out.index[df_out[tax_col].astype(str).str.strip().eq("minor group (<1%)")].tolist()
    if not minor_idx_list:
        raise ValueError("Row 'minor group (<1%)' not found in df_out; cannot compute rankings.")
    cutoff_idx = minor_idx_list[0]

    # rows above cutoff
    upper_df = df_out.iloc[:cutoff_idx].copy()
    upper_df = upper_df[~upper_df[tax_col].astype(str).str.strip().eq("Total reads")]

    upper_num = upper_df.set_index(tax_col)[sample_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)

    # top-k per column
    top_values_by_rank = {str(r): pd.Series(index=sample_cols, dtype="float64") for r in range(1, k + 1)}
    top_taxa_by_rank = {str(r): pd.Series(index=sample_cols, dtype="object") for r in range(1, k + 1)}

    for col in sample_cols:
        s = upper_num[col]
        topk = s.nlargest(k)
        for r_idx in range(1, k + 1):
            if r_idx <= len(topk):
                taxon = topk.index[r_idx - 1]
                val = topk.iloc[r_idx - 1]
                top_values_by_rank[str(r_idx)].loc[col] = float(val)
                top_taxa_by_rank[str(r_idx)].loc[col] = str(taxon) if val > 0 else ""
            else:
                top_values_by_rank[str(r_idx)].loc[col] = pd.NA
                top_taxa_by_rank[str(r_idx)].loc[col] = ""

    colors_count = (upper_num > 0).sum(axis=0)
    row_colors = pd.DataFrame([{tax_col: "# of colors", **colors_count.to_dict()}])

    rows_values = pd.DataFrame([{tax_col: str(r), **top_values_by_rank[str(r)].to_dict()} for r in range(1, k + 1)])
    sum_1_3 = rows_values.set_index(tax_col).loc[["1", "2", "3"], sample_cols].sum(axis=0, numeric_only=True)
    sum_1_5 = rows_values.set_index(tax_col).loc[["1", "2", "3", "4", "5"], sample_cols].sum(axis=0, numeric_only=True)
    row_sum_1_3 = pd.DataFrame([{tax_col: "Σ(1~3) (%)", **sum_1_3.to_dict()}])
    row_sum_1_5 = pd.DataFrame([{tax_col: "Σ(1~5) (%)", **sum_1_5.to_dict()}])

    rows_taxa = pd.DataFrame([{tax_col: str(r), **top_taxa_by_rank[str(r)].to_dict()} for r in range(1, k + 1)])
    return row_colors, rows_values, row_sum_1_3, row_sum_1_5, rows_taxa, top_taxa_by_rank

def append_ranking_rows(df_out: pd.DataFrame,
                        row_colors: pd.DataFrame,
                        rows_values: pd.DataFrame,
                        row_sum_1_3: pd.DataFrame,
                        row_sum_1_5: pd.DataFrame,
                        rows_taxa: pd.DataFrame) -> pd.DataFrame:
    """Append ranking block rows to df_out."""
    blank_vals = {c: pd.NA for c in df_out.columns[1:]}
    row_ranktag = pd.DataFrame([{df_out.columns[0]: "Ranking", **blank_vals}])
    return pd.concat([df_out, row_colors, row_ranktag, rows_values, row_sum_1_3, row_sum_1_5, rows_taxa], ignore_index=True)

def write_sheet_with_formatting(writer, sheet, df_out,
                                top_label, top_taxa_by_rank):
    """
    Write df_out to Excel with:
      - blank leading column,
      - taxonomy label in row 0 col 1 (bold black),
      - coloring of rank rows (1..5) and corresponding top taxa values,
      - correct offsets when using startrow=1.
    """
    # insert blank col at position 0 (entirely empty)
    df_out = df_out.copy()
    df_out.insert(0, "", pd.NA)

    # round numeric cells (data) to 2 decimals
    for c in df_out.columns[2:]:
        df_out[c] = pd.to_numeric(df_out[c], errors="ignore")
        if pd.api.types.is_numeric_dtype(df_out[c]):
            df_out[c] = df_out[c].round(2)

    # write table beginning at row 1 (so row 0 can hold the top taxonomy label)
    df_out.to_excel(writer, sheet_name=sheet, index=False, startrow=1)

    workbook = writer.book
    worksheet = writer.sheets[sheet]

    # put taxonomy label at top-left of taxonomy column (row 0, col 1)
    bold_black = workbook.add_format({"font_color": "black", "bold": True})
    worksheet.write(0, 1, top_label, bold_black)

    # rank formats
    fmt_rank = {rk: workbook.add_format({"font_color": col, "bold": True})
                for rk, col in RANK_COLOR_RGB.items()}

    # column mapping & offsets
    label_col_idx = 1
    label_col_name = df_out.columns[label_col_idx]
    sample_cols_out = list(df_out.columns[2:])
    ROW_OFFSET = 2  # startrow (1) + header (1)

    # locate all '1'..'5' labels in the label column
    rank_row_indices = {
        rk: df_out.index[df_out[label_col_name].astype(str).str.strip().eq(rk)].tolist()
        for rk in ["1", "2", "3", "4", "5"]
    }

    # color first-column labels for both blocks (numeric + taxon names)
    for rk, idx_list in rank_row_indices.items():
        fmt = fmt_rank[rk]
        for r in idx_list:
            worksheet.write(ROW_OFFSET + r, label_col_idx, df_out.iat[r, label_col_idx], fmt)

    # first occurrence of each rank ('numeric' ranking block)
    first_rank_row_idx = {rk: (idx_list[0] if idx_list else None) for rk, idx_list in rank_row_indices.items()}

    # color numeric ranking row cells
    for rk, r in first_rank_row_idx.items():
        if r is None:
            continue
        fmt = fmt_rank[rk]
        for col_name in sample_cols_out:
            j = df_out.columns.get_loc(col_name)
            val = df_out.iat[r, j]
            if isinstance(val, (int, float, np.integer, np.floating)):
                worksheet.write(ROW_OFFSET + r, j, val, fmt)

    # color corresponding top taxa values in the upper part
    for rk, fmt in fmt_rank.items():
        taxa_series = top_taxa_by_rank.get(rk)
        if taxa_series is None:
            continue
        for col_name in sample_cols_out:
            taxon = taxa_series.get(col_name)
            taxon = "" if pd.isna(taxon) else str(taxon)
            if not taxon:
                continue
            matches = df_out.index[df_out[label_col_name].astype(str).str.strip().eq(taxon)].tolist()
            if not matches:
                continue
            r = matches[0]
            j = df_out.columns.get_loc(col_name)
            val = df_out.iat[r, j]
            if isinstance(val, (int, float, np.integer, np.floating)):
                worksheet.write(ROW_OFFSET + r, j, val, fmt)
