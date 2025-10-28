import customtkinter as ctk

class MainWindow(ctk.CTk):
    _instance = None

    @staticmethod
    def show():
        """Show the main window (singleton)."""
        if MainWindow._instance is None:
            MainWindow._instance = MainWindow()
            MainWindow._instance.mainloop()
        else:
            MainWindow._instance.deiconify()

    def __init__(self):
        super().__init__()
        self.title("AI Browser Assistant")
        self.geometry("800x600")
        self.configure(padx=10, pady=10)
        self.create_widgets()

    def create_widgets(self):
        # Title labels
        self.task_label = ctk.CTkLabel(self, text="Tasks", font=("Arial", 16))
        self.task_label.grid(row=0, column=0, sticky="w")
        self.log_label = ctk.CTkLabel(self, text="Logs", font=("Arial", 16))
        self.log_label.grid(row=0, column=1, sticky="w")

        # Text boxes for tasks and logs
        self.task_list = ctk.CTkTextbox(self, width=200)
        self.task_list.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(5, 0))
        self.log_box = ctk.CTkTextbox(self)
        self.log_box.grid(row=1, column=1, sticky="nsew", pady=(5, 0))

        # Configure grid weight to make text boxes expand
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

    def append_log(self, message: str):
        """Append a message to the log box."""
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
