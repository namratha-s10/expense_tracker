import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import database
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expenses Tracker")
        self.root.geometry("800x600")

        # Initialize Database
        database.init_db()

        # Styles
        style = ttk.Style()
        style.theme_use('clam')

        # Main Tab Control
        self.tab_control = ttk.Notebook(root)
        
        self.tab_entry = ttk.Frame(self.tab_control)
        self.tab_dashboard = ttk.Frame(self.tab_control)
        self.tab_view = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab_entry, text='Add Expense')
        self.tab_control.add(self.tab_dashboard, text='Dashboard')
        self.tab_control.add(self.tab_view, text='View Data')
        
        self.tab_control.pack(expand=1, fill="both")

        # Setup Tabs
        self.setup_entry_tab()
        self.setup_dashboard_tab()
        self.setup_view_tab()

        # Bind tab change to refresh data
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def setup_entry_tab(self):
        # Styling
        style = ttk.Style()
        style.configure("Bold.TLabel", font=("Arial", 10, "bold"), background="white")
        style.configure("White.TFrame", background="white")
        style.configure("White.TLabelframe", background="white")
        style.configure("White.TLabelframe.Label", background="white", font=("Arial", 11, "bold"))

        # Main Container with White Background
        self.tab_entry.configure(style="White.TFrame") # Ensure the tab background is white
        
        # Frame
        frame = ttk.LabelFrame(self.tab_entry, text="Log New Expense", padding=20, style="White.TLabelframe")
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # -- Row 0 --
        # Date
        ttk.Label(frame, text="Date (YYYY-MM-DD):", style="Bold.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 5), padx=5)
        self.date_entry = ttk.Entry(frame)
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=0, pady=(0, 15), padx=5, sticky="ew")

        # Amount
        ttk.Label(frame, text="Amount:", style="Bold.TLabel").grid(row=0, column=1, sticky="w", pady=(0, 5), padx=5)
        self.amount_entry = ttk.Entry(frame)
        self.amount_entry.grid(row=1, column=1, pady=(0, 15), padx=5, sticky="ew")

        # -- Row 1 --
        # Category
        ttk.Label(frame, text="Category:", style="Bold.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 5), padx=5)
        self.categories = ["Food", "Transport", "Utilities", "Entertainment", "Shopping", "Health", "Other"]
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(frame, textvariable=self.category_var, values=self.categories)
        self.category_dropdown.current(0)
        self.category_dropdown.grid(row=3, column=0, pady=(0, 15), padx=5, sticky="ew")

        # Note
        ttk.Label(frame, text="Note:", style="Bold.TLabel").grid(row=2, column=1, sticky="w", pady=(0, 5), padx=5)
        self.note_entry = ttk.Entry(frame)
        self.note_entry.grid(row=3, column=1, pady=(0, 15), padx=5, sticky="ew")

        # -- Row 2 --
        # Submit Button
        submit_btn = ttk.Button(frame, text="Add Expense", command=self.add_expense)
        submit_btn.grid(row=4, column=0, columnspan=2, pady=20, sticky="e")

        # Configure Grid Weights
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def setup_dashboard_tab(self):
        self.dashboard_frame = ttk.Frame(self.tab_dashboard, padding=10)
        self.dashboard_frame.pack(fill="both", expand=True)

        # Header Frame for Title and Refresh Button
        header_frame = ttk.Frame(self.dashboard_frame)
        header_frame.pack(fill="x", pady=10)
        
        # Summary Label
        self.summary_label = ttk.Label(header_frame, text="Total Expenses this Month: $0.00", font=("Arial", 14, "bold"))
        self.summary_label.pack(side="left", padx=10)

        # Refresh Button
        refresh_btn = ttk.Button(header_frame, text="Refresh Data", command=self.refresh_dashboard)
        refresh_btn.pack(side="right", padx=10)

        # Matplotlib Figure
        self.figure = plt.Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.dashboard_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def setup_view_tab(self):
        # Treeview
        columns = ("ID", "Date", "Amount", "Category", "Note")
        self.tree = ttk.Treeview(self.tab_view, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            if col == "Note":
                self.tree.column(col, width=200)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons Frame
        btn_frame = ttk.Frame(self.tab_view)
        btn_frame.pack(pady=10)

        # Action Buttons
        edit_btn = ttk.Button(btn_frame, text="Edit Selected", command=self.edit_selected)
        edit_btn.pack(side="left", padx=5)

        delete_btn = ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected)
        delete_btn.pack(side="left", padx=5)

        export_btn = ttk.Button(btn_frame, text="Export to CSV", command=self.export_csv)
        export_btn.pack(side="left", padx=5)

    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
        if confirm:
            item_data = self.tree.item(selected_item)
            record_id = item_data['values'][0]
            database.delete_expense(record_id)
            self.refresh_view()
            messagebox.showinfo("Success", "Record deleted.")

    def edit_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to edit.")
            return

        item_data = self.tree.item(selected_item)
        values = item_data['values']
        record_id = values[0]

        # Create Popup
        popup = tk.Toplevel(self.root)
        popup.title("Edit Expense")
        popup.geometry("400x300")

        # Reuse styling
        frame = ttk.Frame(popup, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Date:").grid(row=0, column=0, pady=5)
        date_entry = ttk.Entry(frame)
        date_entry.insert(0, values[1])
        date_entry.grid(row=0, column=1, pady=5, sticky="ew")

        ttk.Label(frame, text="Amount:").grid(row=1, column=0, pady=5)
        amount_entry = ttk.Entry(frame)
        amount_entry.insert(0, values[2])
        amount_entry.grid(row=1, column=1, pady=5, sticky="ew")

        ttk.Label(frame, text="Category:").grid(row=2, column=0, pady=5)
        category_entry = ttk.Combobox(frame, values=self.categories)
        category_entry.set(values[3])
        category_entry.grid(row=2, column=1, pady=5, sticky="ew")

        ttk.Label(frame, text="Note:").grid(row=3, column=0, pady=5)
        note_entry = ttk.Entry(frame)
        note_entry.insert(0, values[4])
        note_entry.grid(row=3, column=1, pady=5, sticky="ew")

        def save_changes():
            try:
                new_date = date_entry.get()
                new_amount = float(amount_entry.get())
                new_category = category_entry.get()
                new_note = note_entry.get()
                
                database.update_expense(record_id, new_date, new_amount, new_category, new_note)
                self.refresh_view()
                popup.destroy()
                messagebox.showinfo("Success", "Record updated.")
            except ValueError:
                messagebox.showerror("Error", "Invalid Amount")

        save_btn = ttk.Button(frame, text="Save Changes", command=save_changes)
        save_btn.grid(row=4, column=1, pady=20)
    
    def add_expense(self):
        date = self.date_entry.get()
        amount = self.amount_entry.get()
        category = self.category_var.get()
        note = self.note_entry.get()

        if not date or not amount:
            messagebox.showerror("Error", "Date and Amount are required!")
            return

        try:
            amount_float = float(amount)
            database.add_expense(date, amount_float, category, note)
            messagebox.showinfo("Success", "Expense added successfully!")
            self.amount_entry.delete(0, tk.END)
            self.note_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Invalid Amount!")

    def on_tab_change(self, event):
        selected_tab = self.tab_control.select()
        tab_text = self.tab_control.tab(selected_tab, "text")

        if tab_text == "Dashboard":
            self.refresh_dashboard()
        elif tab_text == "View Data":
            self.refresh_view()

    def refresh_dashboard(self):
        # Clear previous plot
        self.ax.clear()
        
        # Fetch data for current month
        today = datetime.date.today()
        rows = database.fetch_expenses_by_month(today.month, today.year)
        
        if not rows:
            self.summary_label.config(text=f"Total Expenses ({today.strftime('%B %Y')}): $0.00")
            self.ax.text(0.5, 0.5, "No Data for this Month", ha='center')
            self.canvas.draw()
            return

        df = pd.DataFrame(rows, columns=["ID", "Date", "Amount", "Category", "Note"])
        total_amount = df["Amount"].sum()
        
        self.summary_label.config(text=f"Total Expenses ({today.strftime('%B %Y')}): ${total_amount:.2f}")

        # Pie Chart
        category_sums = df.groupby("Category")["Amount"].sum()
        self.ax.pie(category_sums, labels=category_sums.index, autopct='%1.1f%%', startangle=90)
        self.ax.set_title("Expenses by Category")
        self.canvas.draw()

    def refresh_view(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        rows = database.fetch_all_expenses()
        for row in rows:
            self.tree.insert("", "end", values=row)

    def export_csv(self):
        rows = database.fetch_all_expenses()
        if not rows:
             messagebox.showinfo("Info", "No data to export.")
             return

        df = pd.DataFrame(rows, columns=["ID", "Date", "Amount", "Category", "Note"])
        filename = "monthly_report.csv"
        df.to_csv(filename, index=False)
        messagebox.showinfo("Success", f"Data exported to {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
