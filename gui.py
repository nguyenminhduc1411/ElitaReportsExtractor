import os
import threading
import customtkinter as ctk
import webbrowser
from tkinter import filedialog, messagebox
from PIL import Image
from processor import process
import json
from tkinter import Menu
import sys
from utils import resource_path
from pathlib import Path
from updater import check_latest
from update_dialog import UpdateDialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from version import APP_NAME, APP_VERSION

ctk.set_appearance_mode("System")
ctk.set_default_color_theme(
    str(resource_path("jj_theme.json"))
)

APP_DIR = Path(os.getenv("LOCALAPPDATA")) / "Elita Reports Extractor"
APP_DIR.mkdir(parents=True, exist_ok=True)

SETTINGS_FILE = APP_DIR / "settings.json"

class SilkGUI(ctk.CTk):

    def __init__(self):

        super().__init__()
        self.create_menu()
        self.iconbitmap(str(resource_path("icon.ico")))
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("720x630")
        self.resizable(False, False)
        self.withdraw()
        self.after(100, self.show_splash)

        self.pdf_var = ctk.StringVar()
        self.output_var = ctk.StringVar()

        self.build_ui()
        self.skip_version = ""
        self.update_dialog_open = False
        self.load_settings()

    # ----------------------------------------------------

    def load_settings(self):

        if SETTINGS_FILE.exists():

            try:

                with open(SETTINGS_FILE, "r", encoding="utf8") as f:
                    data = json.load(f)

                self.pdf_var.set(
                    data.get("pdf_folder", "")
                )

                self.skip_version = data.get(
                    "skip_version",
                    ""
                )

                self.output_var.set(
                    data.get("output_file", "")
                )

                self.open_excel.set(
                    data.get("open_excel", True)
                )

                self.ask_overwrite.set(
                    data.get("ask_before_overwrite", True)
                )

                self.recent_pdf_folders = data.get("recent_pdf_folders", [])

# Tương thích với settings cũ (list[str])
                if (
                    self.recent_pdf_folders
                    and isinstance(self.recent_pdf_folders[0], str)
                ):
                    self.recent_pdf_folders = [
                        {
                            "name": os.path.basename(os.path.normpath(path)),
                            "path": path
                        }
                        for path in self.recent_pdf_folders
                    ]

                self.recent_map = {
                    item["name"]: item["path"]
                    for item in self.recent_pdf_folders
                }

            except:
                pass


    def save_settings(self):

        data = {
            "pdf_folder": self.pdf_var.get(),
            "output_file": self.output_var.get(),
            "open_excel": self.open_excel.get(),
            "ask_before_overwrite": self.ask_overwrite.get(),
            "recent_pdf_folders": self.recent_pdf_folders,
            "skip_version": self.skip_version
        }

        with open(
            SETTINGS_FILE,
            "w",
            encoding="utf8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )

    def add_recent_pdf_folder(self, folder):

        if not folder:
            return

        folder = os.path.normpath(folder)

        name = os.path.basename(folder)

        self.recent_pdf_folders = [
            item
            for item in self.recent_pdf_folders
            if item["path"] != folder
        ]

        self.recent_pdf_folders.insert(
            0,
            {
                "name": name,
                "path": folder
            }
        )

        self.recent_pdf_folders = self.recent_pdf_folders[:5]

        self.recent_map = {
            item["name"]: item["path"]
            for item in self.recent_pdf_folders
        }

        self.recent_combo.configure(
            values=list(self.recent_map.keys())
        )

        self.save_settings()
        
    # ================= MENU =================

    def create_menu(self):

        menubar = Menu(self)

        help_menu = Menu(
            menubar,
            tearoff=0
        )

        help_menu.add_command(
            label="Check for Updates...",
            command=self.check_updates
        )

        help_menu.add_separator()

        help_menu.add_command(
            label="About",
            command=self.show_about
        )

        menubar.add_cascade(
            label="Help",
            menu=help_menu
        )

        self.config(menu=menubar)


    def show_about(self):

        about = ctk.CTkToplevel(self)

        about.title("About")
        about.geometry("420x330")
        about.resizable(False, False)
        about.grab_set()

        ctk.CTkLabel(
            about,
            text="Elita Reports Extractor",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            about,
            text=f"Version {APP_VERSION}",
            font=("Segoe UI", 15)
        ).pack()

        logo = ctk.CTkImage(
            light_image=Image.open(resource_path("elitalogo.png")),
            dark_image=Image.open(resource_path("elitalogo.png")),
            size=(120, 50)      # Có thể chỉnh 100x35 hoặc 140x45
        )

        ctk.CTkLabel(
            about,
            image=logo,
            text=""
        ).pack(pady=(15, 15))

        ctk.CTkLabel(
            about,
            text="Developed by",
            font=("Segoe UI", 14)
        ).pack()

        ctk.CTkLabel(
            about,
            text="Nguyen Minh Duc",
            font=("Segoe UI", 17, "bold")
        ).pack()

        ctk.CTkLabel(
            about,
            text="Application Support Manager - SEA",
            font=("Segoe UI", 13)
        ).pack()

        ctk.CTkLabel(
            about,
            text="Johnson & Johnson Vision",
            font=("Segoe UI", 13)
        ).pack(pady=(0, 15))

        ctk.CTkLabel(
            about,
            text="© 2026 All Rights Reserved",
            font=("Segoe UI", 12)
        ).pack()

        ctk.CTkButton(
            about,
            text="OK",
            width=90,
            command=about.destroy
        ).pack(pady=20)

    # ================= UI =================
    def check_updates(self):

        self.update_window = ctk.CTkToplevel(self)

        self.update_window.title("Check for Updates")

        self.update_window.geometry("300x120")

        self.update_window.grab_set()

        ctk.CTkLabel(
            self.update_window,
            text="Checking for updates..."
        ).pack(pady=30)

        threading.Thread(
            target=self.check_update_thread,
            daemon=True
        ).start()

    def check_update_thread(self):

        try:

            info = check_latest()

            self.after(
                0,
                lambda: self.finish_check(info)
            )

        except Exception as e:

            self.after(
                0,
                lambda: self.update_error(e)
            )    
    
    def finish_check(self, info):

        self.update_window.destroy()

        if info["is_newer"]:

            UpdateDialog(
                self,
                info
            )

        else:
            UpdateDialog(self)

    def update_error(self, e):

        self.update_window.destroy()

        messagebox.showerror(
            "Update Error",
            str(e)
        )
            
    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="Elita Reports Extractor",
            font=("Segoe UI", 24, "bold")
        )

        title.pack(pady=(20, 20))

        # ---------------- PDF Folder ----------------

        frame_pdf = ctk.CTkFrame(self)
        frame_pdf.pack(fill="x", padx=25, pady=10)

        recent_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        recent_frame.pack(
            fill="x",
            padx=25,
            pady=(0,10)
        )

        ctk.CTkLabel(
            recent_frame,
            text="Recent",
            width=90
        ).pack(side="left", padx=10)

        self.recent_combo = ctk.CTkComboBox(
            recent_frame,
            values=list(self.recent_map.keys()) if hasattr(self, "recent_pdf_folders") else [],
            width=430,
            command=self.select_recent_folder
        )

        self.recent_combo.set("Select recent folder...")

        self.recent_combo.pack(side="left", padx=10)

        ctk.CTkLabel(
            frame_pdf,
            text="PDF Folder",
            width=90
        ).pack(side="left", padx=10)

        ctk.CTkEntry(
            frame_pdf,
            textvariable=self.pdf_var,
            width=430
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            frame_pdf,
            text="Browse",
            command=self.select_pdf
        ).pack(side="left")

        # ---------------- Output ----------------

        frame_output = ctk.CTkFrame(self)
        frame_output.pack(fill="x", padx=25, pady=10)

        ctk.CTkLabel(
            frame_output,
            text="Output Folder",
            width=90
        ).pack(side="left", padx=10)

        ctk.CTkEntry(
            frame_output,
            textvariable=self.output_var,
            width=430
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            frame_output,
            text="Browse",
            command=self.select_output
        ).pack(side="left")

     # =================== Checkbox Excel Open ===================

        self.open_excel = ctk.BooleanVar(value=True)
        self.ask_overwrite = ctk.BooleanVar(value=True)

        self.chk_open = ctk.CTkCheckBox(
            self,
            text="Open Excel after finish",
            variable=self.open_excel
        )

        self.chk_open.pack(
            anchor="w",
            padx=35,
            pady=(5, 5)
        )

        self.chk_overwrite = ctk.CTkCheckBox(
            self,
            text="Ask before overwriting existing Excel file",
            variable=self.ask_overwrite
        )

        self.chk_overwrite.pack(
            anchor="w",
            padx=35,
            pady=(0, 15)
        )

        # ====================================================

        # ---------------- Extract Button ----------------

        button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        button_frame.pack(pady=25)

        self.extract_btn = ctk.CTkButton(
            button_frame,
            text="Extract Reports",
            width=220,
            height=42,
            command=self.extract
        )

        self.extract_btn.pack(side="left", padx=5)

        self.open_folder_btn = ctk.CTkButton(
            button_frame,
            text="Open Output Folder",
            width=220,
            height=42,
            state="disabled",
            command=self.open_output_folder
        )

        self.open_folder_btn.pack(side="left", padx=5)

        # ---------------- Progress ----------------

        self.progress = ctk.CTkProgressBar(self)

        self.progress.pack(fill="x", padx=35)

        self.progress.set(0)

        self.progress.configure(
            progress_color="#E52420"
        )

        self.progress_text = ctk.CTkLabel(
        self,
        text="0%"
        )

        self.progress_text.pack(pady=(5,0))

        # ---------------- Status ----------------

        self.status = ctk.CTkLabel(
            self,
            text="Ready to extract reports",
            justify="left",
            anchor="nw",
            height=90
        )

        self.status.pack(
            fill="x",
            padx=35,
            pady=15
        )

        # ---------------- Separator ----------------

        self.separator = ctk.CTkFrame(
            self,
            height=1,
            fg_color="gray70"
        )

        self.separator.pack(
            fill="x",
            padx=35,
            pady=(5, 10)
        )

        # ---------------- Credit ----------------

        self.credit = ctk.CTkLabel(
            self,
            text=(
                "Developed by Nguyen Minh Duc\n"
                "Application Support Manager - SEA\n"
                "Johnson & Johnson Vision - Vietnam\n"
                f"Version {APP_VERSION}" + "© 2026"
            ),
            font=("Segoe UI", 11),
            justify="center",
            text_color="gray50"
        )

        self.credit.pack(
            pady=(0, 10)
        )

        logo = ctk.CTkImage(
            light_image=Image.open(resource_path("elita.png")),
            dark_image=Image.open(resource_path("elita.png")),
            size=(90,90)
        )

        self.logo = ctk.CTkLabel(
            self,
            image=logo,
            text=""
        )

        self.logo.place(
            relx=0.98,
            rely=0.98,
            anchor="se"
        )

    # ----------------------------------------------------

    def select_pdf(self):

        folder = filedialog.askdirectory()

        if folder:

            self.pdf_var.set(folder)
            self.add_recent_pdf_folder(folder)
            self.save_settings()

    def select_recent_folder(self, folder_name):

        folder = self.recent_map.get(folder_name)

        if folder and os.path.isdir(folder):
            self.pdf_var.set(folder)

    # ----------------------------------------------------

    def select_output(self):

        folder = filedialog.askdirectory()

        if folder:

            self.output_var.set(
                os.path.join(folder, "results.xlsx")
            )

            self.save_settings()

    # ----------------------------------------------------

    def update_progress(self, current, total):

        self.after(
            0,
            lambda: self._update_progress(current, total)
        )

    def _update_progress(self, current, total):

        value = current / total if total else 0

        self.progress.set(value)

        percent = int(value * 100)

        self.progress_text.configure(
            text=f"Processing {current} / {total} PDFs ({percent}%)"
        )
    # ----------------------------------------------------

    def update_status(self, text):

        self.after(
        0,
        lambda: self.status.configure(text=text)
        )

    # ----------------------------------------------------

    def extract(self):

        pdf_folder = self.pdf_var.get().strip()
        self.add_recent_pdf_folder(pdf_folder)
        output_file = self.output_var.get().strip()

        if not os.path.isdir(pdf_folder):

            messagebox.showerror(
                "Error",
                "Please select a valid PDF folder."
            )

            return

        if output_file == "":

            messagebox.showerror(
                "Error",
                "Please select output Excel file."
            )

            return

        if (
            os.path.exists(output_file)
            and
            self.ask_overwrite.get()
           ):

            overwrite = messagebox.askyesno(
                "Replace existing file",
                f"The output file already exists.\n\n"
                f"{os.path.basename(output_file)}\n\n"
                f"Do you want to replace it?"
            )

            if not overwrite:
                return

        self.extract_btn.configure(state="disabled")

        self.open_folder_btn.configure(state="disabled")

        self.progress.set(0)

        self.update_status("Processing...")

        threading.Thread(
            target=self.run_extract,
            daemon=True
        ).start()

    def run_extract(self):

        pdf_folder = self.pdf_var.get().strip()
        output_file = self.output_var.get().strip()

        try:

            self.save_settings()

            pdfs, eyes, output_file = process(
                pdf_folder,
                output_file,
                self.update_progress,
                self.update_status
            )

            self.after(
                0,
                lambda: self.finish_success(
                    pdfs,
                    eyes,
                    output_file
                )
            )

        except Exception as e:

            error = str(e)

            self.after(
                0,
                lambda: self.finish_error(error)
            )

        finally:

            self.after(
                0,
                lambda: self.extract_btn.configure(
                    state="normal"
                )
            )
    
    def finish_success(self, pdfs, eyes, output_file):

        self.progress.set(1)

        self.progress.configure(
            progress_color="#2E8B57"
        )

        self.status.configure(
        text=
        "✓ Finished successfully\n\n"
        f"{pdfs} PDFs processed\n"
        f"{eyes} eyes extracted\n\n"
        f"Saved:\n{output_file}"
        )

        self.open_folder_btn.configure(state="normal")

        if self.open_excel.get() and os.path.exists(output_file):
            os.startfile(output_file)

    def finish_error(self, error):

        self.progress.set(0)

        self.progress.configure(
            progress_color="#E52420"
        )

        self.progress_text.configure(
            text="0%"
        )

        self.status.configure(
            text="Ready"
        )

        self.open_folder_btn.configure(
            state="disabled"
        )

        messagebox.showerror(
            "Error",
            error
        )

    def open_output_folder(self):

        output_file = self.output_var.get().strip()

        if os.path.exists(output_file):
            os.startfile(os.path.dirname(output_file))
            
    def show_splash(self):

        self.splash = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=0
        )

        self.splash.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=1
        )

        self.logo_image = ctk.CTkImage(
            light_image=Image.open(resource_path("machine.jpg")),
            dark_image=Image.open(resource_path("machine.jpg")),
            size=(389, 260)
        )

        ctk.CTkLabel(
            self.splash,
            text=APP_NAME,
            font=("Segoe UI", 26, "bold"),
            text_color="black"
        ).pack(pady=(60, 8))

        ctk.CTkLabel(
            self.splash,
            text=f"Version {APP_VERSION}",
            font=("Segoe UI", 16),
            text_color="gray40"
        ).pack()

        ctk.CTkLabel(
            self.splash,
            text="Johnson & Johnson Vision",
            font=("Segoe UI", 13),
            text_color="gray50"
        ).pack(pady=(15, 0))

        ctk.CTkLabel(
            self.splash,
            image=self.logo_image,
            text=""
        ).pack(pady=(15, 0))

        self.status_label = ctk.CTkLabel(
            self.splash,
            text="Initializing...",
            font=("Segoe UI", 12)
        )

        self.status_label.pack(side="bottom", pady=25)

        self.deiconify()

        self.after(3000, self.start_main)

    def hide_splash(self):

        self.splash.destroy()

    def auto_check_updates(self):

        threading.Thread(

            target=self.auto_check_thread,

            daemon=True

        ).start()

    def auto_check_thread(self):

        try:

            info = check_latest()

        except Exception:

            return

        if not info["is_newer"]:
            return

        if info["latest"] == self.skip_version:
            return
        
        self.update_dialog_open = True
        
        self.after(
            0,
            lambda: UpdateDialog(
                self,
                info
            )
        )

    def start_main(self):

        self.hide_splash()

        self.auto_check_updates()