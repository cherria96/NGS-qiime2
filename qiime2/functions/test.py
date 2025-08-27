# demo_priority_dialog.py
import tkinter as tk

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

if __name__ == "__main__":
    # Example labels from metadata
    desc_labels = ["site", "round", "batch", "treatment"]
    priority = prompt_sort_priority(desc_labels)
    print("You selected priority order:", priority)
