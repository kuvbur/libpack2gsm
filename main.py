import pathlib
import tkinter as tk
import webbrowser
from libpack2gsm import main
from tkinter import filedialog, messagebox
from tkinter import ttk

# Версия приложения
APP_VERSION = "v2.1"

# Словарь текстовых переменных
STRINGS = {
    # Переводимые строки
    "i18n": {
        "ru": {
            # Заголовки и метки
            "window_title": "Version Converter v{}",
            "label_app_language": "Interface language:",
            "label_libpack_version": "Версия libpack:",
            "label_lcf_version": "Версия lcf:",
            "label_language": "Язык lcf:",
            "label_source_path": "Путь к libpack:",
            "label_target_path": "Путь к lcf:",
            "label_merge_lcf": "Объединять все пакеты в один LCF",
            
            # Кнопки
            "btn_browse": "Выбрать...",
            "btn_run": "Запустить конвертацию",
            "btn_github": "GitHub",
            
            # Сообщения
            "status_ready": "Готов к работе",
            "status_folder_selected": "Выбрана папка: {}",
            "status_conversion_started": "Конвертация запущена...",
        },
        "en": {
            # Headers and labels
            "window_title": "Version Converter v{}",
            "label_app_language": "Interface language:",
            "label_libpack_version": "Libpack version:",
            "label_lcf_version": "LCF version:",
            "label_language": "LCF language:",
            "label_source_path": "Path to libpack:",
            "label_target_path": "Path to LCF:",
            "label_merge_lcf": "Merge all packages into one LCF",
            
            # Buttons
            "btn_browse": "Browse...",
            "btn_run": "Run conversion",
            "btn_github": "GitHub",
            
            # Messages
            "status_ready": "Ready",
            "status_folder_selected": "Folder selected: {}",
            "status_conversion_started": "Conversion started...",
        }
    },
    
    # Значения combobox (не требуют перевода)
    "version_libpack": ["28", "29"],
    "version_lcf": ["25", "26", "27"],
    "languages": ["RUS", "AUT", "CHE", "CHI", "CZE", "DEN", "FIN", "GER", "GRE", "HUN", "INT", "ITA", 
                  "JPN", "KOR", "NED", "NOR", "NZE", "POL", "POR", "SWE", "TAI", "TUR", "UKI", "UKR", "USA"],
}

# Текущий язык приложения
current_language = 'ru'

# Вспомогательная функция для получения переведённой строки
def _(key):
    return STRINGS['i18n'][current_language].get(key, key)

def browse_folder(entry):
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry.delete(0, tk.END)
        entry.insert(0, folder_path)
        status_var.set(_('status_folder_selected').format(folder_path))

def run_conversion():
    from_version = from_version_combo.get()
    to_version = to_version_combo.get()
    language = language_combo.get()
    source_path = source_path_entry.get()
    target_path = target_path_entry.get()
    merge_lcf = merge_lcf_var.get()
    status_var.set(_('status_conversion_started'))
    main(from_version, to_version, language, source_path, target_path, merge_lcf)


root = tk.Tk()
root.title(_('window_title').format(APP_VERSION))
root.geometry("420x340")
root.resizable(False, False)

# Функция для открытия сайта проекта на GitHub
def open_github():
    webbrowser.open('https://github.com/kuvbur/libpack2gsm')

# Функция для обновления всех элементов интерфейса
def update_ui():
    root.title(_('window_title').format(APP_VERSION))
    lang_label.config(text=_('label_app_language'))
    libpack_version_label.config(text=_('label_libpack_version'))
    lcf_version_label.config(text=_('label_lcf_version'))
    language_label.config(text=_('label_language'))
    source_path_label.config(text=_('label_source_path'))
    target_path_label.config(text=_('label_target_path'))
    source_browse_btn.config(text=_('btn_browse'))
    target_browse_btn.config(text=_('btn_browse'))
    merge_lcf_check.config(text=_('label_merge_lcf'))
    run_btn.config(text=_('btn_run'))
    github_btn.config(text=_('btn_github'))
    status_var.set(_('status_ready'))

# Функция смены языка
def change_language(event=None):
    global current_language
    current_language = lang_combo.get()
    update_ui()

# Метки и элементы ввода
# Строка для выбора языка приложения
lang_label = tk.Label(root, text=_('label_app_language'))
lang_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
lang_combo = ttk.Combobox(root, values=['ru', 'en'], state='readonly', width=5)
lang_combo.current(0)
lang_combo.bind('<<ComboboxSelected>>', change_language)
lang_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)

github_btn = tk.Button(root, text=_('btn_github'), command=open_github, width=8)
github_btn.grid(row=0, column=2, sticky='e', padx=5, pady=5)

libpack_version_label = tk.Label(root, text=_('label_libpack_version'))
libpack_version_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
from_version_combo = ttk.Combobox(root, values=STRINGS['version_libpack'], state="readonly", width=5)
from_version_combo.current(0)
from_version_combo.grid(row=1, column=1, sticky='w', padx=5, pady=5)

lcf_version_label = tk.Label(root, text=_('label_lcf_version'))
lcf_version_label.grid(row=2, column=0, sticky='w', padx=5, pady=5)
to_version_combo = ttk.Combobox(root, values=STRINGS['version_lcf'], state="readonly", width=5)
to_version_combo.current(1)
to_version_combo.grid(row=2, column=1, sticky='w', padx=5, pady=5)

language_label = tk.Label(root, text=_('label_language'))
language_label.grid(row=3, column=0, sticky='w', padx=5, pady=5)
language_combo = ttk.Combobox(root, values=STRINGS['languages'], state="readonly", width=7)
language_combo.current(0)
language_combo.grid(row=3, column=1, sticky='w', padx=5, pady=5)

source_path_label = tk.Label(root, text=_('label_source_path'))
source_path_label.grid(row=4, column=0, sticky='w', padx=5, pady=5)
source_path_entry = tk.Entry(root)
source_path_entry.grid(row=4, column=1, sticky='we', padx=5, pady=5)
source_path_entry.insert(0, str(pathlib.Path(__file__).parent/'libpack'))
source_browse_btn = tk.Button(root, text=_('btn_browse'), command=lambda: browse_folder(source_path_entry), width=10)
source_browse_btn.grid(row=4, column=2, sticky='e', padx=5, pady=5)

target_path_label = tk.Label(root, text=_('label_target_path'))
target_path_label.grid(row=5, column=0, sticky='w', padx=5, pady=5)
target_path_entry = tk.Entry(root)
target_path_entry.grid(row=5, column=1, sticky='we', padx=5, pady=5)
target_path_entry.insert(0, str(pathlib.Path(__file__).parent/'lcf'))
target_browse_btn = tk.Button(root, text=_('btn_browse'), command=lambda: browse_folder(target_path_entry), width=10)
target_browse_btn.grid(row=5, column=2, sticky='e', padx=5, pady=5)

merge_lcf_var = tk.BooleanVar()
merge_lcf_check = tk.Checkbutton(root, text=_('label_merge_lcf'), variable=merge_lcf_var)
merge_lcf_check.grid(row=6, column=0, columnspan=3, sticky='w', padx=5, pady=5)

run_btn = tk.Button(root, text=_('btn_run'), command=run_conversion, width=25)
run_btn.grid(row=7, column=0, columnspan=3, pady=15)

status_var = tk.StringVar()
status_var.set(_('status_ready'))
status_bar = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor='w')
status_bar.grid(row=8, column=0, columnspan=3, sticky='we')

root.grid_columnconfigure(1, weight=1)

root.mainloop()
