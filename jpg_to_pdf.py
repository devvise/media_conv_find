#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import customtkinter as ctk
from PIL import Image
from tkinter import filedialog, messagebox

# Set appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ImageToPDFApp(ctk.CTk):
    """Main application class for the Image to PDF converter."""

    def __init__(self):
        super().__init__()

        self.title("Image to PDF Converter")
        self.geometry("800x500")
        self.minsize(600, 400)

        # State
        self.selected_image: Optional[Path] = None
        self.output_path: Optional[Path] = None

        # Layout configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="CONVERTER",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Image to PDF",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray"
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Stats/Info in sidebar
        self.info_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.info_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="Supported formats:\n- JPG and JPEG\n- PNG\n- GIF",
            justify="left",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.info_label.pack(anchor="w")

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event
        )
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20))
        self.appearance_mode_optionemenu.set("Dark")

        # Create main frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # File Selection Frame
        self.selection_frame = ctk.CTkFrame(self.main_frame)
        self.selection_frame.grid(row=0, column=0, padx=0, pady=(0, 20), sticky="ew")
        self.selection_frame.grid_columnconfigure(0, weight=1)

        self.file_label = ctk.CTkLabel(self.selection_frame, text="Select Source Image:", font=ctk.CTkFont(weight="bold"))
        self.file_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.file_entry = ctk.CTkEntry(self.selection_frame, placeholder_text="No image selected...")
        self.file_entry.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="ew")
        
        self.browse_button = ctk.CTkButton(
            self.selection_frame,
            text="Browse File",
            width=120,
            command=self.choose_image,
            fg_color="#3B8ED0",
            hover_color="#1F538D"
        )
        self.browse_button.grid(row=1, column=1, padx=(0, 20), pady=(0, 20))

        # Conversion Frame
        self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.action_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        self.convert_button = ctk.CTkButton(
            self.action_frame,
            text="Convert to PDF",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.convert_image_to_pdf,
            state="disabled" # Disabled until image is selected
        )
        self.convert_button.pack(fill="x")

        # Result Details
        self.result_frame = ctk.CTkFrame(self.main_frame)
        self.result_frame.grid(row=2, column=0, sticky="nsew")
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.result_frame.grid_rowconfigure(1, weight=1)

        self.result_title = ctk.CTkLabel(self.result_frame, text="Result Details", font=ctk.CTkFont(weight="bold"))
        self.result_title.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        self.empty_result_label = ctk.CTkLabel(
            self.result_frame,
            text="Convert an image to see details here.",
            text_color="gray"
        )
        self.empty_result_label.grid(row=1, column=0, pady=40)

        # Status Bar
        self.status_label = ctk.CTkLabel(self.main_frame, text="Ready", text_color="gray")
        self.status_label.grid(row=3, column=0, sticky="w", pady=(10, 0))

    def change_appearance_mode_event(self, new_appearance_mode: str):
        """Update the appearance mode based on user selection."""
        ctk.set_appearance_mode(new_appearance_mode)

    def get_output_dir(self) -> Path:
        """Get the output directory (Desktop by default, otherwise current working directory)."""
        desktop = Path.home() / "Desktop"
        return desktop if desktop.exists() else Path.cwd()

    def build_output_path(self) -> Path:
        """Return a non-conflicting output path for the generated PDF."""
        output_dir = self.get_output_dir()
        candidate = output_dir / f"{self.selected_image.stem}.pdf"
        counter = 1

        while candidate.exists():
            candidate = output_dir / f"{self.selected_image.stem}_{counter}.pdf"
            counter += 1

        return candidate

    def choose_image(self) -> None:
        """Open a file dialog to allow the user to select an image file."""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif"),
                ("JPG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("GIF", "*.gif"),
            ],
        )

        if not file_path:
            return

        self.selected_image = Path(file_path)
        self.file_entry.delete(0, ctk.END)
        self.file_entry.insert(0, str(self.selected_image))
        self.convert_button.configure(state="normal")
        self.status_label.configure(text=f"Selected: {self.selected_image.name}", text_color="gray")

    def convert_image_to_pdf(self) -> None:
        """Convert the selected image to a PDF and save it to the output directory."""
        if self.selected_image is None:
            return

        self.status_label.configure(text="Converting...", text_color="#3B8ED0")
        self.update_idletasks()

        self.output_path = self.build_output_path()

        try:
            with Image.open(self.selected_image) as img:
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img.save(self.output_path, "PDF")

            self.status_label.configure(text="Conversion successful!", text_color="#2FA572")
            self.show_success_details()

            messagebox.showinfo(
                "Success",
                f"Conversion completed successfully.\n\nFile created at:\n{self.output_path}",
            )
        except Exception as exc:
            self.status_label.configure(text="Conversion failed", text_color="red")
            messagebox.showerror("Error", f"Conversion failed:\n{exc}")

    def show_success_details(self):
        """Display details of the converted PDF file in the results frame."""
        # Clear frame
        for widget in self.result_frame.winfo_children():
            if widget != self.result_title:
                widget.destroy()
        
        file_size_kb = max(1, os.path.getsize(self.output_path) // 1024)
        details_text = f"File Name: {self.output_path.name}\n" \
                       f"Location: {self.output_path.parent}\n" \
                       f"Size: {file_size_kb} KB"

        self.details_label = ctk.CTkLabel(
            self.result_frame,
            text=details_text,
            justify="left",
            anchor="w"
        )
        self.details_label.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="nw")

        self.open_button = ctk.CTkButton(
            self.result_frame,
            text="Open PDF",
            command=lambda: self.open_file(self.output_path)
        )
        self.open_button.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")

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
    app = ImageToPDFApp()
    app.mainloop()
