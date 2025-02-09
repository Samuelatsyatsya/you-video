import yt_dlp
import os
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
    progress_bar.pack()

    # Reset progress values
    downloaded = 0
    total_size = 1
    speed = 0
    download_complete = False

    # Create and start a new thread for the download
    download_thread = threading.Thread(target=perform_download, args=(link, download_folder))
    download_thread.daemon = True  # Ensure the thread will exit when the main program ends
    download_thread.start()

    # Start the GUI update loop
    update_progress()

# Function to perform the download in a separate thread
def perform_download(link, download_folder):
    global downloaded, total_size, speed, download_complete
    ydl_opts = {
        "outtmpl": os.path.join(download_folder, "%(title)s.%(ext)s"),  # Save video with title as filename
        "quiet": True,  # Hide logs
        "noprogress": False,  # Disable yt-dlp built-in progress
        "no_warnings": True,  # Suppress warnings like ffmpeg not found
        "progress_hooks": [progress_hook]  # Use custom progress function
    }

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

    # Display success message
    success_label.config(text=f"Video Downloaded! Saved in: {download_folder}")

    # Display footer message
    footer_label.config(text="Thank you for using YouVideo Downloader! ❤️\nCreated by @little_things\nInspired by MRR KORK, STREET, DR ASSEM, BEN RICHH")

# Function to handle download error
def download_error(error_message):
    messagebox.showerror("Download Error", f"An error occurred: {error_message}")
    status_label.config(text="Download failed!")
    link_entry.config(state=tk.NORMAL)
    download_button.config(state=tk.NORMAL)

# Progress bar function
def progress_hook(d):
    global downloaded, total_size, speed
    if d['status'] == 'downloading':
        # Update progress
        downloaded = d.get('downloaded_bytes', 0)
        total_size = d.get('total_bytes', 1)
        speed = d.get('speed', 0)  # Download speed in bytes per second

# Function to update the progress on the GUI
def update_progress():
    global downloaded, total_size, speed, download_complete

    if not download_complete:
        if total_size > 0:
            # Update progress
            progress = downloaded / total_size * 100
            progress_bar['value'] = progress  # Update the progress bar

            # Calculate download speed in KB/s
            speed_kbps = speed / 1024  # Convert bytes to kilobytes
            speed_label.config(text=f"Speed: {speed_kbps:.2f} KB/s")

            # Update the downloaded size label
            downloaded_size_label.config(text=f"Downloaded: {downloaded / 1024 / 1024:.2f} MB / {total_size / 1024 / 1024:.2f} MB")

        # Schedule the next update
        root.after(100, update_progress)  # Update every 100 ms

# Create the main application window
root = tk.Tk()
root.title("YouVideo Downloader")
root.geometry("600x450")  # Increased height for more space
root.resizable(False, False)  # Lock the window size

# Set the window background color
root.configure(bg='#1E1E1E')  # Dark background for a cool look

# Set the application icon (Make sure you have an icon file like .ico or .png in the path)
root.iconphoto(True, tk.PhotoImage(file='./PeerLearn.png'))  # For cross-platform compatibility (e.g., .png)

# Create the widgets (labels, entry, buttons)
title_label = tk.Label(root, text="YouVideo Downloader", font=("Helvetica", 20), fg="#FFFFFF", bg="#1E1E1E")
title_label.pack(pady=20)

status_label = tk.Label(root, text="Enter the YouTube link below", font=("Helvetica", 12), fg="#FFFFFF", bg="#1E1E1E")
status_label.pack(pady=5)

link_entry = tk.Entry(root, font=("Helvetica", 12), width=50)
link_entry.pack(pady=10)

# Add an 'Enter' press event to start the download
link_entry.bind('<Return>', lambda event: download_video())

download_button = tk.Button(root, text="Download Video", font=("Helvetica", 12), bg="#4CAF50", fg="#FFFFFF", command=download_video)
download_button.pack(pady=10)

# Progress bar setup
progress_bar = ttk.Progressbar(root, length=400, mode='determinate', maximum=100)

# Downloaded size label
downloaded_size_label = tk.Label(root, text="Downloaded: 0 MB", font=("Helvetica", 12), fg="#FFFFFF", bg="#1E1E1E")
downloaded_size_label.pack(pady=5)

# Download speed label
speed_label = tk.Label(root, text="Speed: 0 KB/s", font=("Helvetica", 12), fg="#FFFFFF", bg="#1E1E1E")
speed_label.pack(pady=5)

# Success message after download
success_label = tk.Label(root, text="", font=("Helvetica", 12), fg="#FFFFFF", bg="#1E1E1E")
success_label.pack(pady=10)

# Footer label
footer_label = tk.Label(root, text="", font=("Helvetica", 10), fg="#FFFFFF", bg="#1E1E1E", anchor='center')
footer_label.pack(side=tk.BOTTOM, pady=20)

# Run the Tkinter event loop
root.mainloop()
