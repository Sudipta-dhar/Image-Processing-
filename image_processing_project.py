import cv2
from matplotlib import image
import numpy as np
import os
from tkinter import Tk, Label, Button, filedialog, Frame, Toplevel, LEFT, RIGHT, BOTTOM, messagebox
from PIL import Image, ImageTk
from datetime import datetime
import uuid

class ImageProcessingApp:
    def __init__(self, master):
        self.master = master
        self.center_window(master, 500, 450)
        master.title("Image Processing")

        # Panel 1: Image Selection and Processing
        self.panel1 = Frame(master)
        self.panel1.pack(fill="both", expand=True)

        # Title
        self.label = Label(self.panel1, text="Image Processing", font=("Helvetica", 16), bg='orange', fg='white')
        self.label.pack(fill="x", pady=10)

        # Main content frame
        self.content_frame = Frame(self.panel1)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left side design
        self.left_frame = Frame(self.content_frame)
        self.left_frame.pack(side=LEFT, fill="y", padx=10)

        self.select_image_label = Label(self.left_frame, text="Select Image", font=("Helvetica", 12, "bold"))
        self.select_image_label.pack(pady=5)

        self.take_picture_button = Button(self.left_frame, text="Take Picture", command=self.take_picture)
        self.take_picture_button.pack(pady=5)

        self.instructions_label1 = Label(self.left_frame, text="Take picture using Camera", font=("Helvetica", 10))
        self.instructions_label1.pack(pady=5)
        
        self.choose_picture_button = Button(self.left_frame, text="Choose Picture", command=self.choose_picture)
        self.choose_picture_button.pack(pady=5)

        self.instructions_label2 = Label(self.left_frame, text="Choose picture from files.", font=("Helvetica", 10))
        self.instructions_label2.pack(pady=5)

        # Right side design
        self.right_frame = Frame(self.content_frame)
        self.right_frame.pack(side=RIGHT, fill="y", padx=10)

        self.image_display = Label(self.right_frame)
        self.image_display.pack(pady=5)

        self.image_label = Label(self.right_frame, text="Original Image", font=("Helvetica", 12, "italic"))
        self.image_label.pack(pady=5)

        # Bottom side design
        self.process_button = Button(self.panel1, text="Process Image", command=self.process_image)
        self.process_button.pack(side=BOTTOM, pady=10)

        self.image_path = None
        self.cv_image = None
        self.processed_images = []

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f'{width}x{height}+{x}+{y}')

    def take_picture(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open camera.")
            return

        ret, frame = cap.read()
        cap.release()

        if ret:
            self.image_path = "captured_image.jpg"
            cv2.imwrite(self.image_path, frame)
            self.cv_image = frame
            self.show_image(self.image_path)
        else:
            messagebox.showerror("Error", "Could not capture image.")

    def choose_picture(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if self.image_path:
            self.cv_image = cv2.imread(self.image_path)
            self.show_image(self.image_path)

    def show_image(self, path):
        image = Image.open(path)
        image = image.resize((250, 250), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.image_display.config(image=photo)
        self.image_display.image = photo
        self.image_label.config(text=os.path.basename(path))

    def process_image(self):
        if self.cv_image is None:
            messagebox.showerror("Error", "No image selected.")
            return

        self.panel2 = Toplevel(self.master)
        self.center_window(self.panel2, 800, 700)
        self.panel2.title("Processed Images")

        label = Label(self.panel2, text="Image Processing", font=("Helvetica", 16), bg='orange', fg='white')
        label.pack(fill="x", pady=10)

        self.result_frame = Frame(self.panel2)
        self.result_frame.pack(pady=10)

        save_button = Button(self.panel2, text="Save Images", command=self.save_images, bg='green', fg='white', font=("Arial", 12, "italic", "bold"))
        save_button.pack(side="bottom", anchor="se", padx=10, pady=10)

        image = self.cv_image
        self.processed_images.clear()

        # Processing functions
        processes = [
            ("Grayscale", lambda img: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)),
            ("Gaussian Blur", lambda img: cv2.GaussianBlur(img, (15, 15), 0)),
            ("Edge Detection", lambda img: cv2.Canny(img, 100, 200)),
            ("Threshold", lambda img: cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY)[1]),
            ("Dilation", lambda img: cv2.dilate(cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY)[1], np.ones((5, 5), np.uint8), iterations=1)),
            ("Erosion", lambda img: cv2.erode(cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY)[1], np.ones((5, 5), np.uint8), iterations=1)),
            ("Opening", lambda img: cv2.morphologyEx(cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY)[1], cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))),
            ("Closing", lambda img: cv2.morphologyEx(cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY)[1], cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))),
            ("Gradient", lambda img: cv2.morphologyEx(cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY)[1], cv2.MORPH_GRADIENT, np.ones((5, 5), np.uint8))),
            ("Top Hat", lambda img: cv2.morphologyEx(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.MORPH_TOPHAT, np.ones((5, 5), np.uint8))),
            ("Black Hat", lambda img: cv2.morphologyEx(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.MORPH_BLACKHAT, np.ones((5, 5), np.uint8))),
            ("Histogram Equalization", lambda img: cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))),
            ("Adaptive Threshold", lambda img: cv2.adaptiveThreshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)),
            ("Laplacian", lambda img: cv2.convertScaleAbs(cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F))),
            ("Bilateral Filter", lambda img: cv2.bilateralFilter(img, 15, 75, 75))
        ]

        # Display processed images
        for i, (name, func) in enumerate(processes):
            try:
                processed_image = func(image)
                if len(processed_image.shape) == 2:  # if grayscale, convert to RGB for display
                    processed_image = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2BGR)
                self.processed_images.append((name, processed_image))
            except Exception as e:
                messagebox.showerror("Error", f"Error processing {name}: {e}")
                continue

            image_pil = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
            image_pil = image_pil.resize((150, 150), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image_pil)

            row = i // 5
            col = i % 5

            image_label = Label(self.result_frame, image=photo)
            image_label.image = photo  # keep a reference!
            image_label.grid(row=row * 2, column=col, padx=5, pady=5)

            label = Label(self.result_frame, text=name)
            label.grid(row=row * 2 + 1, column=col, padx=5, pady=5)

        self.result_frame.pack()

    def save_images(self):
        save_dir = r"C:\Users\sudipta\Desktop\image_pp\image_pp\process_pictures"
        os.makedirs(save_dir, exist_ok=True)

        for name, img in self.processed_images:
            unique_id = uuid.uuid4()
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{name}_{timestamp}_{unique_id}.jpg"
            filepath = os.path.join(save_dir, filename)
            cv2.imwrite(filepath, img)
        messagebox.showinfo("Info", f"All images saved to {save_dir}")

if __name__ == "__main__":
    root = Tk()
    app = ImageProcessingApp(root)
    root.mainloop()
