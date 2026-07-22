import customtkinter as ctk
import webbrowser
from version import RELEASES_URL
from updater import (
    download_update,
    run_installer
)

import threading
from tkinter import messagebox

class UpdateDialog(ctk.CTkToplevel):

    def __init__(self, parent, info=None):

        super().__init__(parent)

        self.parent = parent

        self.info = info

        if info:

            self.title("Update Available")

        else:

            self.title("Software Updates")

        if info:

            self.geometry("560x520")

        else:

            self.geometry("420x300")

        self.resizable(False, False)

        self.grab_set()

        self.build_ui()


    def build_ui(self):

        if self.info is None:

            self.build_no_update()

            return

        ctk.CTkLabel(
            self,
            text="🚀 Update Available",
            font=("Segoe UI",24,"bold")
        ).pack(
            pady=(20,10)
        )

        ctk.CTkLabel(
            self,
            text=f"Current Version : {self.info['current']}",
            font=("Segoe UI",15)
        ).pack()

        ctk.CTkLabel(
            self,
            text=f"Latest Version : {self.info['latest']}",
            font=("Segoe UI",15,"bold")
        ).pack()
        
        ctk.CTkLabel(
            self,
            text="What's New",
            font=("Segoe UI",16,"bold")
        ).pack(pady=(5,5))

        textbox = ctk.CTkTextbox(
            self,
            width=500,
            height=200
        )

        textbox.pack()

        self.progress = ctk.CTkProgressBar(
            self,
            width=500
        )

        self.progress.pack(
            pady=(15,5)
        )

        self.progress.set(0)

        self.progress_label = ctk.CTkLabel(
            self,
            text=""
        )

        self.progress_label.pack()

        notes = []

        for line in self.info["notes"].splitlines():

            if line.startswith("<img"):
                continue

            notes.append(line)

        textbox.insert(
            "1.0",
            "\n".join(notes)
        )

        textbox.configure(
            state="disabled"
        )


        frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        frame.pack(
            pady=20
        )

        self.skip_var = ctk.BooleanVar(value=False)

        self.skip_checkbox = ctk.CTkCheckBox(

            self,

            text="Don't remind me again for this version",

            variable=self.skip_var

        )

        self.skip_checkbox.pack(
            padx=20,
            pady=(5,10),
            anchor="w"
        )

        self.download_btn = ctk.CTkButton(
            frame,
            text="Download & Install",
            width=150,
            command=self.download
        )

        self.download_btn.pack(
            side="left",
            padx=8
        )

        self.later_btn = ctk.CTkButton(
            frame,
            text="Remind Me Later",
            width=120,
            command=self.later
        )

        self.later_btn.pack(
            side="left",
            padx=8
        )

    def build_no_update(self):

        ctk.CTkLabel(
            self,
            text="✓",
            font=("Segoe UI", 52, "bold"),
            text_color="green"
        ).pack(
            pady=(30, 5)
        )

        ctk.CTkLabel(
            self,
            text="Elita Reports Extractor",
            font=("Segoe UI", 24, "bold")
        ).pack()

        ctk.CTkLabel(
            self,
            text=f"Version {__import__('version').APP_VERSION}",
            font=("Segoe UI", 16)
        ).pack(
            pady=(5, 15)
        )

        ctk.CTkLabel(
            self,
            text="You're using the latest version.",
            font=("Segoe UI", 15)
        ).pack(
            pady=(0, 30)
        )

        frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        frame.pack(pady=20)

        ctk.CTkButton(
            frame,
            text="Release Notes",
            width=150,
            command=self.open_release_notes
        ).pack(
            side="left",
            padx=8
        )

        ctk.CTkButton(
            frame,
            text="OK",
            width=100,
            command=self.destroy
        ).pack(
            side="left",
            padx=8
        )
        
    def download(self):

        self.download_btn.configure(
            text="Downloading...",
            state="disabled"
        )

        self.later_btn.configure(
            state="disabled"
        )

        self.protocol(
            "WM_DELETE_WINDOW",
            lambda: None
        )

        self.progress.configure(
            progress_color="#E52420"
        )

        self.progress.set(0)

        self.progress_label.configure(
            text="Starting download..."
        )

        threading.Thread(
            target=self.download_thread,
            daemon=True
        ).start()

    def open_release_notes(self):

        if self.info:

            webbrowser.open(self.info["url"])

        else:

            webbrowser.open(RELEASES_URL)

    def later(self):

        if self.skip_var.get():

            self.master.skip_version = self.info["latest"]

            self.master.save_settings()

        self.destroy()
        
    def download_thread(self):

        try:

            installer = download_update(
                self.info["download"],
                self.update_progress
            )

            self.after(
                0,
                lambda: self.download_finished(
                    installer
                )
            )

        except Exception as e:

            self.after(
                0,
                lambda: messagebox.showerror(
                    "Download Error",
                    str(e)
                )
            )
    
    def download_finished(self, installer):

        # Cho phép đóng cửa sổ trở lại
        self.protocol(
            "WM_DELETE_WINDOW",
            self.destroy
        )

        self.installer = installer

        self.progress.set(1)

        self.progress.configure(
            progress_color="#2E8B57"
        )

        self.progress_label.configure(
            text="Download completed."
        )

        self.download_btn.configure(
            text="Install Update",
            state="normal",
            command=self.install_update
        )

        self.later_btn.configure(
            text="Close",
            state="normal"
        )

    def update_progress(self, current, total):

        self.after(
            0,
            lambda: self._update_progress(
                current,
                total
            )
        )

    def _update_progress(self, current, total):

        value = current / total

        self.progress.set(value)

        percent = int(value * 100)

        current_mb = current / 1024 / 1024

        total_mb = total / 1024 / 1024

        self.progress_label.configure(

            text=f"{percent}%   ({current_mb:.1f} / {total_mb:.1f} MB)"

        )

    def install_update(self):

        self.download_btn.configure(
            state="disabled"
        )

        self.later_btn.configure(
            state="disabled"
        )

        self.progress_label.configure(
            text="Launching installer..."
        )

        self.after(
            500,
            self.finish_install
        )

    def finish_install(self):

        self.master.skip_version = ""

        self.master.save_settings()

        run_installer(self.installer)

        self.master.destroy()   

    def destroy(self):

        self.parent.update_dialog_open = False

        super().destroy()