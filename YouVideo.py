import yt_dlp
import os
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading  # Import threading for background execution
import time

# Global variables for download progress
downloaded = 0
total_size = 1
speed = 0
download_complete = False

def get_format_selector():
    # yt-dlp format selector string:
    # prefer 720p MP4 and, if ffmpeg exists, allow separate video+audio merge.
    if shutil.which("ffmpeg"):
        return "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]"
    return "best[height<=720][ext=mp4]/best[height<=720]"

def rounded_rect(canvas, x1, y1, x2, y2, r=18, **kwargs):
    # Draw a rounded rectangle by smoothing a polygon path.
    points = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

class RoundedButton(tk.Canvas):
    # Canvas-based button so we can draw rounded corners and custom hover states.
    def __init__(self, parent, text, command, width=160, height=44, radius=18,
                 bg="#ff2d55", fg="#ffffff", hover_bg="#e11d48", disabled_bg="#fca5a5",
                 font=("Poppins", 11, "bold")):
        super().__init__(parent, width=width, height=height, bg=parent.cget("bg"),
                         highlightthickness=0, bd=0)
        self._text = text
        self._command = command
        self._radius = radius
        self._bg = bg
        self._fg = fg
        self._hover_bg = hover_bg
        self._disabled_bg = disabled_bg
        self._font = font
        self._state = "normal"
        self._hover = False
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self._draw()

    def _current_bg(self):
        if self._state != "normal":
            return self._disabled_bg
        return self._hover_bg if self._hover else self._bg

    def _draw(self):
        self.delete("all")
        w = int(self["width"])
        h = int(self["height"])
        rounded_rect(self, 0, 0, w, h, r=self._radius, fill=self._current_bg(), outline="")
        self.create_text(w / 2, h / 2, text=self._text, fill=self._fg, font=self._font)

    def _on_enter(self, _event):
        self._hover = True
        self._draw()

    def _on_leave(self, _event):
        self._hover = False
        self._draw()

    def _on_click(self, _event):
        if self._state == "normal" and self._command:
            self._command()

    def config(self, **kwargs):
        state = kwargs.get("state")
        if state is not None:
            self._state = "normal" if state == tk.NORMAL else "disabled"
            self._draw()

    configure = config

# Function to download video and show progress bar
def download_video():
    global downloaded, total_size, speed, download_complete
    link = link_entry.get()
    if not link:
        messagebox.showwarning("Input Error", "Please enter a YouTube link.")
        return
    
    # Set up the download folder
    download_folder = os.path.join(os.path.expanduser("~"), "Downloads")

    # Show message that download is starting
    status_label.config(text="Initializing Download...")

    # Disable the input field and the download button while downloading
    link_entry.config(state=tk.DISABLED)
    download_button.config(state=tk.DISABLED)

    # Show progress bar
    progress_bar.grid()

    # Reset progress values
    downloaded = 0
    total_size = 1
    speed = 0
    download_complete = False

    # Run the download in a background thread so the UI never freezes.
    download_thread = threading.Thread(target=perform_download, args=(link, download_folder))
    download_thread.daemon = True  # Ensure the thread will exit when the main program ends
    download_thread.start()

    # Start the GUI update loop
    update_progress()

# Function to perform the download in a separate thread
def perform_download(link, download_folder):
    global downloaded, total_size, speed, download_complete
    # yt-dlp options that control output, progress, and format.
    ydl_opts = {
        "outtmpl": os.path.join(download_folder, "%(title)s.%(ext)s"),  # Save video with title as filename
        "quiet": True,  # Hide logs
        "noprogress": False,  # Disable yt-dlp built-in progress
        "no_warnings": True,  # Suppress warnings like ffmpeg not found
        "progress_hooks": [progress_hook],  # Use custom progress function
        "format": get_format_selector(),
    }
    # Only set merge output when ffmpeg is available (needed to combine video+audio).
    if shutil.which("ffmpeg"):
        ydl_opts["merge_output_format"] = "mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        # Get the path to the downloaded file
        file_name = ydl.prepare_filename(ydl.extract_info(link, download=False))
        file_path = os.path.join(download_folder, file_name)

        # Set the modification time of the downloaded file to the current time
        current_time = time.time()  # Get the current time in seconds since epoch
        os.utime(file_path, (current_time, current_time))  # Set the access and modification time

        # Update status and re-enable inputs after download finishes (on main thread)
        root.after(0, update_ui_on_complete, download_folder)

    except Exception as e:
        # Handle any download errors (on main thread)
        root.after(0, download_error, str(e))

# Function to update UI after download is complete
def update_ui_on_complete(download_folder):
    global download_complete
    download_complete = True
    status_label.config(text="Download complete!")
    link_entry.config(state=tk.NORMAL)
    download_button.config(state=tk.NORMAL)
    link_entry.delete(0, tk.END)

    # Display success message
    success_label.config(text=f"Video Downloaded! Saved in: {download_folder}")

    # Footer stays static (no change needed on completion)

# Function to handle download error
def download_error(error_message):
    messagebox.showerror("Download Error", f"An error occurred: {error_message}")
    status_label.config(text="Download failed!")
    link_entry.config(state=tk.NORMAL)
    download_button.config(state=tk.NORMAL)

# Progress bar hook (called by yt-dlp from the download thread)
def progress_hook(d):
    global downloaded, total_size, speed
    if d['status'] == 'downloading':
        # Update progress
        downloaded = d.get('downloaded_bytes') or 0
        total_size = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
        speed = d.get('speed') or 0  # Download speed in bytes per second

# Function to update the progress on the GUI (main thread via after)
def update_progress():
    global downloaded, total_size, speed, download_complete

    if not download_complete:
        if total_size > 0:
            # Update progress
            progress = downloaded / total_size * 100
            progress_bar['value'] = progress  # Update the progress bar

            # Calculate download speed in KB/s
            speed_kbps = (speed or 0) / 1024  # Convert bytes to kilobytes
            speed_label.config(text=f"Speed: {speed_kbps:.2f} KB/s")

            # Update the downloaded size label
            downloaded_size_label.config(text=f"Downloaded: {downloaded / 1024 / 1024:.2f} MB / {total_size / 1024 / 1024:.2f} MB")

        # Schedule the next update on the Tkinter event loop
        root.after(100, update_progress)  # Update every 100 ms

# Create the main application window
root = tk.Tk()
root.title("YouVideo Downloader")
root.geometry("720x560")
root.resizable(False, False)

# Palette
BG = "#f6f7fb"
CARD = "#ffffff"
TEXT = "#0f172a"
MUTED = "#64748b"
BRAND = "#ff2d55"
BRAND_DARK = "#e11d48"
BORDER = "#e5e7eb"
SOFT_1 = "#eef2ff"
SOFT_2 = "#ffe4e6"
SOFT_3 = "#ecfeff"
INPUT_BG = "#f8fafc"

root.configure(bg=BG)

# Set the application icon if available (prevents crash if the file is missing)
icon_path = "./PeerLearn.png"
if os.path.exists(icon_path):
    try:
        root.iconphoto(True, tk.PhotoImage(file=icon_path))  # For cross-platform compatibility (e.g., .png)
    except Exception:
        pass

# TTK styling
style = ttk.Style()
style.theme_use("clam")
style.configure("App.Horizontal.TProgressbar", troughcolor=SOFT_1, background=BRAND, thickness=8)

# Background canvas lets us place soft shapes and rounded cards.
canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Soft background shapes
canvas.create_oval(-140, -120, 280, 300, fill=SOFT_1, outline="")
canvas.create_oval(470, 20, 880, 430, fill=SOFT_2, outline="")
canvas.create_oval(420, 360, 820, 740, fill=SOFT_3, outline="")

# Header area
header = tk.Frame(canvas, bg=BG)
brand_icon = tk.Canvas(header, width=34, height=34, bg=BG, highlightthickness=0)
brand_icon.create_oval(2, 2, 32, 32, fill=BRAND, outline="")
brand_icon.create_polygon(14, 10, 26, 17, 14, 24, fill="white", outline="")
brand_icon.grid(row=0, column=0, rowspan=2, padx=(0, 12))

title_label = tk.Label(header, text="YouVideo", fg=TEXT, bg=BG, font=("Poppins", 24, "bold"))
title_label.grid(row=0, column=1, sticky="w")
title_suffix = tk.Label(header, text="Downloader", fg=BRAND, bg=BG, font=("Poppins", 12, "bold"))
title_suffix.grid(row=0, column=2, sticky="w", padx=(8, 0))

subtitle_label = tk.Label(header, text="Clean, fast, and reliable YouTube downloads.", fg=MUTED, bg=BG, font=("Poppins", 11))
subtitle_label.grid(row=1, column=1, columnspan=2, sticky="w", pady=(2, 0))

quality_label = tk.Label(header, text="Quality: 720p max", fg=BRAND, bg=BG, font=("Poppins", 9, "bold"))
quality_label.grid(row=2, column=1, sticky="w", pady=(6, 0))

status_label = tk.Label(header, text="Paste a link to get started.", fg=TEXT, bg=BG, font=("Poppins", 11))
status_label.grid(row=3, column=1, columnspan=2, sticky="w", pady=(6, 0))

# Absolute placement on the canvas for precise layout.
canvas.create_window(48, 36, window=header, anchor="nw")

# Card container layout constants (manual positioning for crisp spacing).
CARD_X = 48
CARD_Y = 160
CARD_W = 624
CARD_H = 300
INNER_PAD = 24
INNER_W = CARD_W - (INNER_PAD * 2)
BUTTON_W = 170
ENTRY_W = INNER_W - BUTTON_W - 12

# Draw the rounded card background, then place widgets on top of it.
rounded_rect(canvas, CARD_X, CARD_Y, CARD_X + CARD_W, CARD_Y + CARD_H, r=20, fill=CARD, outline=BORDER, width=1)

card_inner = tk.Frame(canvas, bg=CARD)
canvas.create_window(CARD_X + INNER_PAD, CARD_Y + 20, window=card_inner, anchor="nw", width=INNER_W)

card_title = tk.Label(card_inner, text="Video link", fg=TEXT, bg=CARD, font=("Poppins", 12, "bold"))
card_title.grid(row=0, column=0, sticky="w")

card_sub = tk.Label(card_inner, text="Saved to your Downloads folder.", fg=MUTED, bg=CARD, font=("Poppins", 10))
card_sub.grid(row=1, column=0, sticky="w", pady=(2, 12))

form_row = tk.Frame(card_inner, bg=CARD)
form_row.grid(row=2, column=0, sticky="w")

entry_shell = tk.Canvas(form_row, width=ENTRY_W, height=44, bg=CARD, highlightthickness=0)
rounded_rect(entry_shell, 0, 0, ENTRY_W, 44, r=14, fill=INPUT_BG, outline=BORDER, width=1)
# Embed a normal Entry inside the rounded canvas.
link_entry = tk.Entry(entry_shell, bd=0, bg=INPUT_BG, fg=TEXT, insertbackground=TEXT, font=("Poppins", 11))
entry_shell.create_window(12, 11, window=link_entry, anchor="nw", width=ENTRY_W - 24, height=22)
entry_shell.grid(row=0, column=0, padx=(0, 12))

# Add an 'Enter' press event to start the download
link_entry.bind("<Return>", lambda event: download_video())

download_button = RoundedButton(form_row, text="Download Video", command=download_video,
                                width=BUTTON_W, height=44, radius=16,
                                bg=BRAND, hover_bg=BRAND_DARK)
download_button.grid(row=0, column=1, sticky="e")

# Progress bar setup
progress_bar = ttk.Progressbar(card_inner, style="App.Horizontal.TProgressbar", mode="determinate", maximum=100, length=INNER_W)
progress_bar.grid(row=3, column=0, sticky="ew", pady=(18, 6))
# Hide until a download starts.
progress_bar.grid_remove()

stats_row = tk.Frame(card_inner, bg=CARD)
stats_row.grid(row=4, column=0, sticky="ew")
stats_row.columnconfigure(0, weight=1)
stats_row.columnconfigure(1, weight=1)

# Downloaded size label
downloaded_size_label = tk.Label(stats_row, text="Downloaded: 0 MB", fg=TEXT, bg=CARD, font=("Poppins", 10))
downloaded_size_label.grid(row=0, column=0, sticky="w")

# Download speed label
speed_label = tk.Label(stats_row, text="Speed: 0 KB/s", fg=TEXT, bg=CARD, font=("Poppins", 10))
speed_label.grid(row=0, column=1, sticky="e")

# Success message after download
success_label = tk.Label(card_inner, text="", fg=BRAND, bg=CARD, font=("Poppins", 10, "bold"))
success_label.grid(row=5, column=0, sticky="w", pady=(10, 0))

# Footer label (static attribution)
footer_label = tk.Label(
    canvas,
    text="Created by @little_things\nInspired by MRR KORK, STREET, DR ASSEM, ADZAH BERNARD",
    fg=MUTED,
    bg=BG,
    font=("Poppins", 9),
    anchor="center",
)
canvas.create_window(360, 530, window=footer_label)

# Run the Tkinter event loop
root.mainloop()
