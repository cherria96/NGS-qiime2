import pandas as pd
import tkinter as tk
from typing import Dict, List
from functions.config import SITE_ORDER_BASE

def prompt_sort_priority(desc_labels):
    """
    GUI dialog to choose sort priority from desc_labels.
    Returns a list of labels in priority order.
    """
    root = tk.Tk()
    root.title("Choose sorting priority")
    root.geometry("520x320")
    root.resizable(False, False)

    tk.Label(root, text="Available").grid(row=0, column=0, padx=8, pady=6)
    tk.Label(root, text="Priority (top = highest)").grid(row=0, column=2, padx=8, pady=6)

    lb_avail = tk.Listbox(root, selectmode=tk.SINGLE, height=11)
    lb_prio  = tk.Listbox(root, selectmode=tk.SINGLE, height=11)
    lb_avail.grid(row=1, column=0, rowspan=6, padx=8, pady=4, sticky="ns")
    lb_prio.grid(row=1, column=2, rowspan=6, padx=8, pady=4, sticky="ns")

    for lab in desc_labels:
        lb_avail.insert(tk.END, lab)

    def add_to_prio():
        sel = lb_avail.curselection()
        if not sel: return
        val = lb_avail.get(sel[0])
        if val not in lb_prio.get(0, tk.END):
            lb_prio.insert(tk.END, val)

    def remove_from_prio():
        sel = lb_prio.curselection()
        if not sel: return
        lb_prio.delete(sel[0])

    def move(up=True):
        sel = lb_prio.curselection()
        if not sel: return
        i = sel[0]
        j = i-1 if up else i+1
        if j < 0 or j >= lb_prio.size(): return
        val = lb_prio.get(i)
        lb_prio.delete(i)
        lb_prio.insert(j, val)
        lb_prio.select_set(j)

    result = []
    def on_ok():
        nonlocal result
        result = list(lb_prio.get(0, tk.END))
        root.destroy()

    def on_cancel():
        nonlocal result
        result = []
        root.destroy()

    tk.Button(root, text="Add", width=4, command=add_to_prio).grid(row=2, column=1, pady=2)
    tk.Button(root, text="Remove", width=4, command=remove_from_prio).grid(row=3, column=1, pady=2)
    tk.Button(root, text="Up", width=4, command=lambda: move(True)).grid(row=4, column=1, pady=2)
    tk.Button(root, text="Down", width=4, command=lambda: move(False)).grid(row=5, column=1, pady=2)

    tk.Button(root, text="OK", width=10, command=on_ok).grid(row=7, column=1, pady=8)
    tk.Button(root, text="Cancel", width=10, command=on_cancel).grid(row=8, column=1, pady=2)

    root.mainloop()
    return result

def prompt_value_order_for_label(label, values):
    """
    Show a small dialog to choose the order for the unique values of a label.
    Returns the ordered list (highest priority first).
    Returns None if user skips (label will not be used for sorting).
    Falls back to console if Tkinter isn't available.
    """
    # De-duplicate while preserving original order
    seen = set()
    values = [v for v in values if not (v in seen or seen.add(v))]

    try:
        import tkinter as tk

        root = tk.Tk()
        root.title(f"Order values for: {label}")
        root.geometry("560x360")
        root.resizable(False, False)

        tk.Label(root, text=f"Available values for '{label}'").grid(row=0, column=0, padx=8, pady=6)
        tk.Label(root, text="Order (top = first)").grid(row=0, column=2, padx=8, pady=6)

        lb_avail = tk.Listbox(root, selectmode=tk.SINGLE, height=12, exportselection=False)
        lb_prio  = tk.Listbox(root, selectmode=tk.SINGLE, height=12, exportselection=False)
        lb_avail.grid(row=1, column=0, rowspan=6, padx=8, pady=4, sticky="ns")
        lb_prio.grid(row=1, column=2, rowspan=6, padx=8, pady=4, sticky="ns")

        for v in values:
            lb_avail.insert(tk.END, v)

        def add_to_prio():
            sel = lb_avail.curselection()
            if not sel: return
            val = lb_avail.get(sel[0])
            if val not in lb_prio.get(0, tk.END):
                lb_prio.insert(tk.END, val)

        def remove_from_prio():
            sel = lb_prio.curselection()
            if not sel: return
            lb_prio.delete(sel[0])

        def move(up=True):
            sel = lb_prio.curselection()
            if not sel: return
            i = sel[0]
            j = i-1 if up else i+1
            if j < 0 or j >= lb_prio.size(): return
            val = lb_prio.get(i)
            lb_prio.delete(i)
            lb_prio.insert(j, val)
            lb_prio.select_set(j)

        tk.Button(root, text="Add", width=4, command=add_to_prio).grid(row=2, column=1, pady=2)
        tk.Button(root, text="Remove", width=4, command=remove_from_prio).grid(row=3, column=1, pady=2)
        tk.Button(root, text="Up", width=4, command=lambda: move(True)).grid(row=4, column=1, pady=2)
        tk.Button(root, text="Down", width=4, command=lambda: move(False)).grid(row=5, column=1, pady=2)

        result = []

        def on_ok():
            nonlocal result
            # If user didn't pick anything, treat as skip (None)
            result = list(lb_prio.get(0, tk.END)) or None
            root.destroy()

        def on_skip():
            nonlocal result
            result = None
            root.destroy()

        tk.Button(root, text="OK", width=10, command=on_ok).grid(row=8, column=1, pady=8)
        tk.Button(root, text="Skip", width=10, command=on_skip).grid(row=9, column=1, pady=2)

        root.mainloop()
        return result

    except Exception:
        # Headless fallback: console prompts
        print(f"\n[Headless] Order values for '{label}'. Unique values:")
        print(", ".join(values))
        print("Enter a comma-separated order (or press Enter to skip):")
        try:
            raw = input("> ").strip()
            if not raw:
                return None
            chosen = [x.strip() for x in raw.split(",") if x.strip() in values]
            return chosen or None
        except EOFError:
            return None
        
def get_site_order(meta_df, site_col="site"):
    """
    Return the site order:
    - Start with predefined SITE_ORDER_BASE
    - Append any unseen sites from metadata at the end (in the order they appear)
    """
    seen = set(SITE_ORDER_BASE)
    all_sites = meta_df[site_col].astype(str).unique().tolist()
    extras = [s for s in all_sites if s not in seen]
    return SITE_ORDER_BASE + extras

def get_user_sort_spec_from_metadata(meta_df, sampleid_col='sampleid'):
    """
    Step 1: let the user prioritize which labels to use (site, round, ...).
    Step 2: for each chosen label, ask the user to order its unique values.
    Returns: { label -> [ordered values] }
    """
    if sampleid_col not in meta_df.columns:
        raise ValueError(f"Metadata is missing '{sampleid_col}'.")
    # Candidate labels = all metadata fields except sampleid
    candidate_labels = [c for c in meta_df.columns if c != sampleid_col]

    # --- Step 1: ask which labels to prioritize ---
    priority_labels = prompt_sort_priority(candidate_labels)
    print("Chosen label order:", priority_labels)

    sort_spec: Dict[str, List[str]] = {}

    # --- Step 2: for each label, ask value order ---
    for label in priority_labels:
        if label.lower() == 'site':
            site_order = get_site_order(meta_df, site_col="site")
            sort_spec[label] = site_order
            print(f"using preconfigured site order: {site_order}")
        else:
            vals = meta_df[label].astype(str).unique().tolist()
            ordered = prompt_value_order_for_label(label, vals)  # list[str] or None
            if ordered is not None:
                sort_spec[label] = ordered

    return sort_spec

def compute_global_sample_order(
    meta_df: pd.DataFrame,
    sort_spec: Dict[str, List[str]],
    sampleid_col: str = "sampleid",
) -> List[str]:
    """
    Produce a global ordered list of sample IDs based on sort_spec.
    Any sample whose value isn't listed gets ranked after listed ones for that label.
    """
    meta = meta_df.astype(str).drop_duplicates(subset=[sampleid_col], keep="first")
    sids = meta[sampleid_col].tolist()

    # Precompute rank maps: label -> {value -> rank}, then {sid -> rank}
    label_value_rank: Dict[str, Dict[str, int]] = {
        lab: {v: i for i, v in enumerate(vals)} for lab, vals in sort_spec.items()
    }
    sid_rank_per_label: Dict[str, Dict[str, int]] = {}
    for lab, v2r in label_value_rank.items():
        lab_map = dict(zip(meta[sampleid_col], meta[lab].astype(str)))
        sid_rank_per_label[lab] = {sid: v2r.get(lab_map.get(sid, ""), 10**9) for sid in sids}

    labels_in_order = list(sort_spec.keys())

    def key_for_sid(sid: str):
        return tuple(sid_rank_per_label[lab][sid] for lab in labels_in_order)

    return sorted(sids, key=key_for_sid)

def apply_global_sample_order_to_df(
    df: pd.DataFrame,
    global_sample_order: List[str],
) -> pd.DataFrame:
    """
    Reorder the *sample columns* of df according to global_sample_order.
    - Keeps non-sample columns at the front (0 or 2 lead columns depending on your pipeline).
    - Columns not present in metadata/global list are appended at the end (original order).
    """
    out = df.copy()

    # detect layout
    if out.columns[0] == "":
        sample_start = 2
    else:
        sample_start = 1

    sample_cols = list(out.columns[sample_start:])
    # intersection in the order of the global list
    ordered_present = [c for c in global_sample_order if c in sample_cols]
    # keep any "unknown" samples (not in meta/global list) at the end, preserving original order
    unknown = [c for c in sample_cols if c not in set(global_sample_order)]

    new_cols = list(out.columns[:sample_start]) + ordered_present + unknown
    return out.reindex(columns=new_cols)



