import os
import shutil
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, filedialog

# Function to get directories from the user
def get_directory():
    def on_ok():
        # Accessing variables from outer function
        nonlocal screenshot_dir, enemy_present_dir, no_enemy_present_dir
        # Retrieving directory paths from the input fields
        screenshot_dir = screenshot_entry.get()
        enemy_present_dir = enemy_present_entry.get()
        no_enemy_present_dir = no_enemy_present_entry.get()
        # Closing the Tkinter window
        root.destroy()
        
    screenshot_dir = None
    enemy_present_dir = None
    no_enemy_present_dir = None

    # Creating Tkinter window
    root = tk.Tk()
    root.title("Enemy or Not - By BigH")

    # Labels and input fields for directory selection
    tk.Label(root, text="Select Directories", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=3, pady=10)

    tk.Label(root, text="Screenshot Directory:").grid(row=1, column=0, padx=5, pady=5)
    screenshot_entry = tk.Entry(root, width=50)
    screenshot_entry.grid(row=1, column=1, padx=5, pady=5)
    tk.Button(root, text="Browse", command=lambda: screenshot_entry.insert(tk.END, filedialog.askdirectory()), width=10).grid(row=1, column=2, padx=5, pady=5)

    tk.Label(root, text="Directory for Images with Enemy:").grid(row=2, column=0, padx=5, pady=5)
    enemy_present_entry = tk.Entry(root, width=50)
    enemy_present_entry.grid(row=2, column=1, padx=5, pady=5)
    tk.Button(root, text="Browse", command=lambda: enemy_present_entry.insert(tk.END, filedialog.askdirectory()), width=10).grid(row=2, column=2, padx=5, pady=5)

    tk.Label(root, text="Directory for Images without Enemy:").grid(row=3, column=0, padx=5, pady=5)
    no_enemy_present_entry = tk.Entry(root, width=50)
    no_enemy_present_entry.grid(row=3, column=1, padx=5, pady=5)
    tk.Button(root, text="Browse", command=lambda: no_enemy_present_entry.insert(tk.END, filedialog.askdirectory()), width=10).grid(row=3, column=2, padx=5, pady=5)

    # Button to start annotation process
    tk.Button(root, text="Start Annotation", command=on_ok, bg="green", fg="white").grid(row=4, column=1, pady=10)

    # Button to display explanation
    explanation_button = tk.Button(root, text="Explanation", command=display_explanation)
    explanation_button.grid(row=0, column=2, padx=5, pady=5, sticky="ne")

    root.mainloop()

    return screenshot_dir, enemy_present_dir, no_enemy_present_dir

# Function to start annotating images
def start_annotation(screenshot_dir, enemy_present_dir, no_enemy_present_dir):
    # List all files in the screenshot directory
    screenshot_files = os.listdir(screenshot_dir)

    # Creating Tkinter window for annotation
    root = tk.Tk()
    root.title("Screenshot Annotation Tool")
    root.geometry("550x700")

    # Function to annotate each image
    def annotate_image(annotation):
        # Accessing variable from outer function
        nonlocal idx
        # Move the image to the appropriate directory based on annotation
        if annotation == "enemy_present":
            shutil.move(os.path.join(screenshot_dir, screenshot_files[idx]), os.path.join(enemy_present_dir, screenshot_files[idx]))
        elif annotation == "no_enemy_present":
            shutil.move(os.path.join(screenshot_dir, screenshot_files[idx]), os.path.join(no_enemy_present_dir, screenshot_files[idx]))
        idx += 1
        # Display the next image or show completion message
        if idx < len(screenshot_files):
            display_image(idx)
        else:
            messagebox.showinfo("Annotation Complete", "All images have been annotated.")
            root.destroy()

    # Function to display the current image
    def display_image(idx):
        # Open the image, resize it, and display it
        image_path = os.path.join(screenshot_dir, screenshot_files[idx])
        image = Image.open(image_path)
        image = image.resize((500, 500))
        photo = ImageTk.PhotoImage(image)

        image_label.config(image=photo)
        image_label.image = photo

    # Label to display the image
    image_label = tk.Label(root)
    image_label.pack(pady=20)

    # Buttons for annotation
    tk.Button(root, text="Enemy Present", command=lambda: annotate_image("enemy_present"), bg="green", fg="white", font=("Helvetica", 16), width=15, height=2).pack(side=tk.LEFT, padx=20)
    tk.Button(root, text="No Enemy Present", command=lambda: annotate_image("no_enemy_present"), bg="red", fg="white", font=("Helvetica", 16), width=15, height=2).pack(side=tk.RIGHT, padx=20)

    idx = 0
    display_image(idx)

    root.mainloop()

# Function to display explanation
def display_explanation():
    explanation_pages = [
       """
        Page 1: Introduction

        Welcome to the Screenshot Annotation Tool!

        This tool allows you to categorize images into "enemy present" and "no enemy present" categories. 
        Before starting, make sure you have created two separate folders: one for images with enemies 
        and another for images without enemies. You will need to specify these folders during the setup process.

        Below, you'll find a brief overview of how to use this tool:

        Click the 'Next' button to continue.
        """,
        """
        Page 2: Select Directories

        To get started, you need to select directories where your screenshots are located, 
        where images with enemies will be moved, and where images without enemies will be moved. 

        Click the 'Browse' button next to each field to select the directories. If you accidentally
        selected the wrong directory, you can highlight the current path, delete it, and then click 
        the 'Browse' button again to choose the correct directory.

        Click the 'Next' button to continue.
        """,
        """
        Page 3: Start Annotation

        Once you've selected directories, click the 'Start Annotation' button to begin annotating your images. 
        For each image, click 'Enemy Present' if there's an enemy in the image, 
        or 'No Enemy Present' if there's no enemy. Continue annotating until all images are processed.

        Click the 'Next' button to close the explanation.
        """
    ]

    # Function to navigate through explanation pages
    def next_page():
        nonlocal page_number
        page_number += 1
        if page_number < len(explanation_pages):
            explanation_label.config(text=explanation_pages[page_number])
        else:
            root.destroy()

    page_number = 0

    # Creating Tkinter window for explanation
    root = tk.Toplevel()
    root.title("Explanation")
    
    explanation_label = tk.Label(root, text=explanation_pages[page_number], wraplength=600, justify="left")
    explanation_label.pack(padx=20, pady=20)

    next_button = tk.Button(root, text="Next", command=next_page)
    next_button.pack(pady=10)

    root.mainloop()

# Initializing variables for directory paths
screenshot_dir = None
enemy_present_dir = None
no_enemy_present_dir = None

# Getting directory paths from the user
screenshot_dir, enemy_present_dir, no_enemy_present_dir = get_directory()

# If directories are selected, start the annotation process
if screenshot_dir and enemy_present_dir and no_enemy_present_dir:
    start_annotation(screenshot_dir, enemy_present_dir, no_enemy_present_dir)