#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import customtkinter as ctk
from tkinter import filedialog, messagebox

# Set appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PDFFinderApp(ctk.CTk):
    """Main application class for the PDF Finder utility."""

    def __init__(self):
        super().__init__()

        self.title("PDF Finder")
        self.geometry("1000x650")
        self.minsize(800, 500)

        # State
        self.selected_folder: Optional[Path] = None

        # Layout configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="PDF FINDER",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Recursive PDF Search",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray"
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))
        self.appearance_mode_optionemenu.set("Dark")

        # Create main frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # Search Controls Frame
        self.controls_frame = ctk.CTkFrame(self.main_frame)
        self.controls_frame.grid(row=0, column=0, padx=0, pady=(0, 20), sticky="ew")
        self.controls_frame.grid_columnconfigure(1, weight=1)

        # Folder Selection
        self.folder_label = ctk.CTkLabel(self.controls_frame, text="Source Folder:", font=ctk.CTkFont(weight="bold"))
        self.folder_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.folder_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="Select a directory to search...")
        self.folder_entry.grid(row=1, column=0, columnspan=2, padx=(20, 10), pady=(0, 20), sticky="ew")
        
        self.folder_button = ctk.CTkButton(
            self.controls_frame,
            text="Browse",
            width=100,
            command=self.choose_folder,
            fg_color="#3B8ED0",
            hover_color="#1F538D"
        )
        self.folder_button.grid(row=1, column=2, padx=(0, 20), pady=(0, 20))

        # Keyword Search
        self.keyword_label = ctk.CTkLabel(self.main_frame, text="Filter by Keyword:", font=ctk.CTkFont(weight="bold"))
        self.keyword_label.grid(row=1, column=0, padx=0, pady=(0, 5), sticky="w")

        self.search_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.search_frame.grid(row=2, column=0, sticky="new", pady=(0, 10))
        self.search_frame.grid_columnconfigure(0, weight=1)

        self.keyword_entry = ctk.CTkEntry(self.search_frame, placeholder_text="e.g. invoice, report, 2023...")
        self.keyword_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.keyword_entry.bind("<Return>", lambda e: self.search_pdf())

        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="Search PDFs",
            command=self.search_pdf,
            font=ctk.CTkFont(weight="bold")
        )
        self.search_button.grid(row=0, column=1)

        # Results area
        self.results_label = ctk.CTkLabel(self.main_frame, text="Matching Results:", font=ctk.CTkFont(weight="bold"))
        self.results_label.grid(row=3, column=0, padx=0, pady=(10, 5), sticky="w")

        # Scrollable list of results
        self.results_scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Files Found")
        self.results_scrollable_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        self.main_frame.grid_rowconfigure(4, weight=1)

        self.status_label = ctk.CTkLabel(self.main_frame, text="Ready", text_color="gray")
        self.status_label.grid(row=5, column=0, sticky="w")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        """Update the appearance mode based on user selection."""
        ctk.set_appearance_mode(new_appearance_mode)

    def choose_folder(self) -> None:
        """Open a directory dialog to allow the user to select the folder to search."""
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        self.selected_folder = Path(folder_path)
        self.folder_entry.delete(0, ctk.END)
        self.folder_entry.insert(0, str(self.selected_folder))
        self.status_label.configure(text=f"Selected: {self.selected_folder.name}", text_color="gray")

    def search_pdf(self) -> None:
        """Search for PDF files in the selected folder, filtering by keyword if provided."""
        if self.selected_folder is None:
            messagebox.showerror("Error", "Please select a folder first.")
            return

        if not self.selected_folder.exists():
            messagebox.showerror("Error", "The selected folder does not exist.")
            return

        keyword = self.keyword_entry.get().strip().lower()

        # Clear previous results
        for widget in self.results_scrollable_frame.winfo_children():
            widget.destroy()

        self.status_label.configure(text="Searching...", text_color="#3B8ED0")
        self.update_idletasks()

        matches = []
        try:
            for pdf_path in self.selected_folder.rglob("*"):
                if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
                    continue

                file_name = pdf_path.name.lower()
                if not keyword or keyword in file_name:
                    matches.append(pdf_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error accessing files: {e}")
            self.status_label.configure(text="Error occurred", text_color="red")
            return

        if not matches:
            self.status_label.configure(text="No PDF files found.", text_color="orange")
            no_results = ctk.CTkLabel(self.results_scrollable_frame, text="No matches found in this directory.")
            no_results.pack(pady=20)
            return

        for path in sorted(matches):
            file_frame = ctk.CTkFrame(self.results_scrollable_frame, fg_color="transparent")
            file_frame.pack(fill="x", padx=5, pady=2)

            # File name label
            file_label = ctk.CTkLabel(
                file_frame,
                text=path.name,
                anchor="w",
                font=ctk.CTkFont(weight="bold")
            )
            file_label.pack(side="left", padx=10)

            # File path label (smaller)
            path_label = ctk.CTkLabel(
                file_frame,
                text=str(path.parent),
                text_color="gray",
                font=ctk.CTkFont(size=10),
                anchor="w"
            )
            path_label.pack(side="left", fill="x", expand=True)

            # Open button
            open_btn = ctk.CTkButton(
                file_frame,
                text="Open",
                width=60,
                height=24,
                command=lambda p=path: self.open_file(p)
            )
            open_btn.pack(side="right", padx=10)

        self.status_label.configure(text=f"Found {len(matches)} files.", text_color="#2FA572")

    def open_file(self, path: Path) -> None:
        """Open a file using the default system application."""
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(path))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(path)], check=False)
            else:
                subprocess.run(["xdg-open", str(path)], check=False)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not open file:\n{exc}")


if __name__ == "__main__":
    app = PDFFinderApp()
    app.mainloop()
