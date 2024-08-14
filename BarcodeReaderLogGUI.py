import customtkinter as ctk
import time
import threading
import os
import psutil
import pystray
from pystray import MenuItem as item
from PIL import Image
from queue import Queue

# pyinstaller -F --paths=C:\Projects\BarcodeReaderLogGUI\.venv\Lib\site-packages C:\Projects\BarcodeReaderLogGUI\BarcodeReaderLogGUI.py --noconsole

# python setup.py build
class BarcodeReaderApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self._set_appearance_mode("dark")
        self.title("Barcode Reader")
        self.geometry("725x460")
        self.configure(bg="#252525")
        self.iconbitmap("C:\\cpi\\barcode\\img\\logo.ico")
        self.resizable(0, 0)

        # Widgets
        self.create_widgets()

        # Queue for thread-safe communication
        self.queue = Queue()

        # Start a background thread to update the label
        self.stop_thread = False
        self.thread = threading.Thread(target=self.update_label_from_file)
        self.thread.start()

        self.check_process_thread = threading.Thread(target=self.check_process)
        self.check_process_thread.start()

        # Periodically check the queue for updates
        self.process_queue()

        # Hide the main window at startup
        self.withdraw()

        # Start the system tray in a separate thread
        tray_thread = threading.Thread(target=self.setup_tray)
        tray_thread.daemon = True
        tray_thread.start()

        self.bind("<Unmap>", self.on_minimize)


    def create_widgets(self):

        self.label_prog = ctk.CTkLabel(self, text="Program name:", fg_color="#252525", text_color="#FFFFFF")
        self.label_prog.grid(row=0, column=0, pady=10, padx=55, sticky="w")  # Aligning to the left
        self.text_area_prog = ctk.CTkTextbox(self, width=650, height=25, wrap="word")
        self.text_area_prog.grid(row=1, column=0, columnspan=3, pady=10, padx=20, sticky="w")

        self.label_reader = ctk.CTkLabel(self, text="Reader: ", fg_color="#252525", text_color="#FFFFFF")
        self.label_reader.grid(row=2, column=0, pady=10, padx=95, sticky="w")  # Aligning to the left

        # Reader Text Area
        self.text_area = ctk.CTkTextbox(self, width=200, height=250, wrap="word")
        self.text_area.grid(row=3, column=0, pady=10, padx=20, sticky="w")

        # AOI Label
        self.label_aoi = ctk.CTkLabel(self, text="AOI:", fg_color="#252525", text_color="#FFFFFF")
        self.label_aoi.grid(row=2, column=1, pady=10, padx=95, sticky="w")  # Aligning to the left

        # AOI Text Area
        self.text_area_aoi = ctk.CTkTextbox(self, width=200, height=250, wrap="word")
        self.text_area_aoi.grid(row=3, column=1, pady=10, padx=20, sticky="w")

        # VVTS Label
        self.label_vvts = ctk.CTkLabel(self, text="VVTS: ", fg_color="#252525", text_color="#FFFFFF")
        self.label_vvts.grid(row=2, column=2, pady=10, padx=95, sticky="w")  # Aligning to the left

        # VVTS Text Area
        self.text_area_vvts = ctk.CTkTextbox(self, width=200, height=250, wrap="word")
        self.text_area_vvts.grid(row=3, column=2, pady=10, padx=20, sticky="w")

        self.label_process_status = ctk.CTkLabel(self, text="Process Status: Checking... ", fg_color="#252525",
                                                 text_color="#FFFFFF")
        self.label_process_status.grid(row=4, column=0, columnspan=3, pady=10, padx=55, sticky="w")

        # Add a restart button
        self.restart_button = ctk.CTkButton(self, text="Restart Process", command=self.restart_process)
        self.restart_button.grid(row=5, column=0, columnspan=3, pady=20)

    def process_queue(self):
        try:
            while not self.queue.empty():
                action = self.queue.get_nowait()
                action()
        except Queue.Empty:
            pass
        self.after(100, self.process_queue)  # Check the queue every 100 ms

    def update_label_from_file(self):
        last_position_reader = 0
        last_position_aoi = 0
        last_position_vvts = 0
        last_position_prog = 0
        while not self.stop_thread:
            try:
                # reader
                with open('C:\\cpi\\barcode\\log\\readerLog.txt', 'r') as file:
                    file.seek(last_position_reader)
                    new_data = file.read()
                    last_position_reader = file.tell()

                    if new_data:
                        for line in new_data.splitlines():
                            part = line.split(";")
                            if "Barcode0" in line:
                                self.queue.put(lambda: self.text_area.insert(ctk.END, part[0] + " "))
                                self.queue.put(lambda: self.text_area.insert(ctk.END, part[2] + " ", 'highlight'))
                                self.queue.put(lambda: self.text_area.insert(ctk.END, part[1] + "\n\n"))
                            else:
                                self.queue.put(lambda: self.text_area.insert(ctk.END, part[0] + " "))
                                self.queue.put(lambda: self.text_area.insert(ctk.END, part[2] + " "))
                                self.queue.put(lambda: self.text_area.insert(ctk.END, part[1] + "\n\n"))
                        self.queue.put(lambda: self.text_area.see(ctk.END))  # Scroll to the end
            except FileNotFoundError:
                pass
            time.sleep(1)

            # aoi
            try:
                with open('C:\\cpi\\barcode\\log\\AOILog.txt', 'r') as file:
                    file.seek(last_position_aoi)
                    new_data = file.read()
                    last_position_aoi = file.tell()

                    if new_data:
                        for line in new_data.splitlines():
                            part = line.split(";")
                            if "Barcode0" in line:
                                self.queue.put(lambda: self.text_area_aoi.insert(ctk.END, part[0] + " "))
                                self.queue.put(lambda: self.text_area_aoi.insert(ctk.END, part[2] + " ", 'highlight'))
                                self.queue.put(lambda: self.text_area_aoi.insert(ctk.END, part[1] + "\n\n"))
                            else:
                                self.queue.put(lambda: self.text_area_aoi.insert(ctk.END, part[0] + " "))
                                self.queue.put(lambda: self.text_area_aoi.insert(ctk.END, part[2] + " "))
                                self.queue.put(lambda: self.text_area_aoi.insert(ctk.END, part[1] + "\n\n"))
                        self.queue.put(lambda: self.text_area_aoi.see(ctk.END))  # Scroll to the end
            except FileNotFoundError:
                pass
            time.sleep(1)

            # vvts
            try:
                with open('C:\\cpi\\barcode\\log\\VVTSLog.txt', 'r') as file:
                    file.seek(last_position_vvts)
                    new_data = file.read()
                    last_position_vvts = file.tell()

                    if new_data:
                        for line in new_data.splitlines():
                            part = line.split(";")
                            if "Barcode0" in line:
                                self.queue.put(lambda: self.text_area_vvts.insert(ctk.END, part[0] + " "))
                                self.queue.put(lambda: self.text_area_vvts.insert(ctk.END, part[2] + " ", 'highlight'))
                                self.queue.put(lambda: self.text_area_vvts.insert(ctk.END, part[1] + "\n\n"))
                            else:
                                self.queue.put(lambda: self.text_area_vvts.insert(ctk.END, part[0] + " "))
                                self.queue.put(lambda: self.text_area_vvts.insert(ctk.END, part[2] + " "))
                                self.queue.put(lambda: self.text_area_vvts.insert(ctk.END, part[1] + "\n\n"))
                        self.queue.put(lambda: self.text_area_vvts.see(ctk.END))  # Scroll to the end

            except FileNotFoundError:
                pass
            time.sleep(1)

            # prog
            try:
                with open('C:\\cpi\\barcode\\log\\progLog.txt', 'r') as file:
                    file.seek(last_position_prog)
                    new_data = file.read()
                    last_position_prog = file.tell()

                    if new_data:
                        for line in new_data.splitlines():
                            part = line.split(";")
                            self.queue.put(lambda: self.text_area_prog.insert(ctk.END, "\n" + part[0] + " "))
                            self.queue.put(lambda: self.text_area_prog.insert(ctk.END, part[1] + " "))
                        self.queue.put(lambda: self.text_area_prog.see(ctk.END))  # Scroll to the end
            except FileNotFoundError:
                pass
            time.sleep(1)

    def check_process(self):
        process_name = "main.exe"  # Replace with the actual process name you want to check
        while not self.stop_thread:
            process_running = any(proc.name() == process_name for proc in psutil.process_iter())
            if process_running:
                self.queue.put(
                    lambda: self.label_process_status.configure(text="Process Status: Running ", text_color="green"))
            else:
                self.queue.put(
                    lambda: self.label_process_status.configure(text="Process Status: Not Running ", text_color="red"))
            time.sleep(5)

    def restart_process(self):
        process_name = "C:\\cpi\\barcode\\main.exe"
        # Terminate the process if running
        for proc in psutil.process_iter():
            if proc.name() == process_name:
                proc.terminate()
                proc.wait()  # Wait for the process to terminate
        # Restart the process
        os.startfile(process_name)

    def on_minimize(self, event=None):
        """Minimize the window to the system tray."""
        if self.state() == "iconic":
            self.withdraw()

    def setup_tray(self):
        icon_image = Image.open("C:\\cpi\\barcode\\img\\logo.ico")  # Replace with the correct path to your .ico file
        icon = pystray.Icon('barcode_reader', icon_image, menu=pystray.Menu(
            item('Open', lambda: self.deiconify()),
            item('Quit', self.quit_app)
        ))
        icon.run()

    def quit_app(self):
        self.stop_thread = True
        self.thread.join()
        self.check_process_thread.join()
        self.destroy()

    def on_closing(self):
        self.withdraw()  # Hide the window instead of closing
        # Optionally, stop the threads and the app
        self.quit_app()

    # def on_closing(self):
    #     self.stop_thread = True
    #     self.thread.join()
    #     self.check_process_thread.join()
    #     self.destroy()


if __name__ == "__main__":
    app = BarcodeReaderApp()
    app.text_area.tag_config('highlight', foreground="red")  # Highlight lines with "barcode0" in red
    app.text_area_aoi.tag_config('highlight', foreground="red")  # Highlight lines with "barcode0" in red
    app.text_area_vvts.tag_config('highlight', foreground="red")  # Highlight lines with "barcode0" in red
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
