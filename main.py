import pathlib
import tkinter as tk
from libpack2gsm import main
from tkinter import filedialog, messagebox
from tkinter import ttk

def browse_folder(entry):
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry.delete(0, tk.END)
        entry.insert(0, folder_path)
        status_var.set(f"Выбрана папка: {folder_path}")

def run_conversion():
    from_version = from_version_combo.get()
    to_version = to_version_combo.get()
    language = language_combo.get()
    source_path = source_path_entry.get()
    target_path = target_path_entry.get()
    merge_lcf = merge_lcf_var.get()
    status_var.set("Конвертация запущена...")
    main(from_version, to_version, language, source_path, target_path, merge_lcf)


root = tk.Tk()
root.title("Конвертер версий")
root.geometry("400x280")
root.resizable(False, False)

# Метки и элементы ввода
tk.Label(root, text="Версия libpack:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
from_version_combo = ttk.Combobox(root, values=["28"], state="readonly", width=5)
from_version_combo.current(0)
from_version_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)

tk.Label(root, text="Версия lcf:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
to_version_combo = ttk.Combobox(root, values=["25", "26", "27"], state="readonly", width=5)
to_version_combo.current(1)
to_version_combo.grid(row=1, column=1, sticky='w', padx=5, pady=5)

tk.Label(root, text="Язык lcf:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
languages = ["RUS","AUT","CHE","CHI","CZE","DEN","FIN","GER","GRE","HUN","INT","ITA","JPN","KOR","NED",
             "NOR","NZE","POL","POR","SWE","TAI","TUR","UKI","UKR","USA"]
language_combo = ttk.Combobox(root, values=languages, state="readonly", width=7)
language_combo.current(0)
language_combo.grid(row=2, column=1, sticky='w', padx=5, pady=5)

tk.Label(root, text="Путь к libpack:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
source_path_entry = tk.Entry(root)
source_path_entry.grid(row=3, column=1, sticky='we', padx=5, pady=5)
source_path_entry.insert(0, str(pathlib.Path(__file__).parent/'libpack'))
source_browse_btn = tk.Button(root, text="Выбрать...", command=lambda: browse_folder(source_path_entry), width=10)
source_browse_btn.grid(row=3, column=2, sticky='e', padx=5, pady=5)

tk.Label(root, text="Путь к lcf:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
target_path_entry = tk.Entry(root)
target_path_entry.grid(row=4, column=1, sticky='we', padx=5, pady=5)
target_path_entry.insert(0, str(pathlib.Path(__file__).parent/'lcf'))
target_browse_btn = tk.Button(root, text="Выбрать...", command=lambda: browse_folder(target_path_entry), width=10)
target_browse_btn.grid(row=4, column=2, sticky='e', padx=5, pady=5)

merge_lcf_var = tk.BooleanVar()
merge_lcf_check = tk.Checkbutton(root, text="Объединять все пакеты в один LCF", variable=merge_lcf_var)
merge_lcf_check.grid(row=5, column=0, columnspan=3, sticky='w', padx=5, pady=5)

run_btn = tk.Button(root, text="Запустить конвертацию", command=run_conversion, width=25)
run_btn.grid(row=6, column=0, columnspan=3, pady=15)

status_var = tk.StringVar()
status_var.set("Готов к работе")
status_bar = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor='w')
status_bar.grid(row=7, column=0, columnspan=3, sticky='we')

root.grid_columnconfigure(1, weight=1)

root.mainloop()
