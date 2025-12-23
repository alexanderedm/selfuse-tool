
import customtkinter as ctk
import time
import threading
from tkinter import messagebox

class TimerWindow:
    def __init__(self, tk_root=None, on_timer_complete=None):
        self.tk_root = tk_root
        self.window = None
        self.on_timer_complete = on_timer_complete
        self.running = False
        self.remaining_seconds = 0
        self.timer_thread = None

    def show(self):
        if self.window is not None:
             try:
                 self.window.lift()
                 self.window.focus_force()
                 return
             except:
                 self.window = None

        if self.tk_root:
            self.window = ctk.CTkToplevel(self.tk_root)
        else:
            self.window = ctk.CTk()

        self.window.title("⏲️ 倒數計時器")
        self.window.geometry("400x350")
        self.window.resizable(False, False)
        
        # UI Components
        self._create_ui()
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_ui(self):
        # Title Input
        self.title_var = ctk.StringVar(value="計時器")
        title_entry = ctk.CTkEntry(
            self.window, 
            textvariable=self.title_var,
            placeholder_text="輸入提醒標題",
            font=("Microsoft JhengHei UI", 14),
            height=40
        )
        title_entry.pack(fill="x", padx=20, pady=(20, 10))

        # Time Input Frame
        time_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        time_frame.pack(pady=10)

        # Hours
        self.hours_var = ctk.StringVar(value="00")
        ctk.CTkEntry(time_frame, textvariable=self.hours_var, width=50, font=("msg", 24), justify="center").pack(side="left", padx=5)
        ctk.CTkLabel(time_frame, text=":", font=("msg", 24)).pack(side="left")
        
        # Minutes
        self.minutes_var = ctk.StringVar(value="00")
        ctk.CTkEntry(time_frame, textvariable=self.minutes_var, width=50, font=("msg", 24), justify="center").pack(side="left", padx=5)
        ctk.CTkLabel(time_frame, text=":", font=("msg", 24)).pack(side="left")

        # Seconds
        self.seconds_var = ctk.StringVar(value="00")
        ctk.CTkEntry(time_frame, textvariable=self.seconds_var, width=50, font=("msg", 24), justify="center").pack(side="left", padx=5)

        # Control Buttons
        btn_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        btn_frame.pack(pady=20)

        self.start_btn = ctk.CTkButton(btn_frame, text="開始", command=self.start_timer, width=80)
        self.start_btn.pack(side="left", padx=10)

        self.stop_btn = ctk.CTkButton(btn_frame, text="停止", command=self.stop_timer, width=80, fg_color="red", state="disabled")
        self.stop_btn.pack(side="left", padx=10)

        self.reset_btn = ctk.CTkButton(btn_frame, text="重設", command=self.reset_timer, width=80, fg_color="gray")
        self.reset_btn.pack(side="left", padx=10)

        # Progress Label
        self.status_label = ctk.CTkLabel(self.window, text="準備就緒", font=("Microsoft JhengHei UI", 12))
        self.status_label.pack(pady=10)

        # Progress Bar
        self.progress = ctk.CTkProgressBar(self.window)
        self.progress.pack(fill="x", padx=20, pady=10)
        self.progress.set(0)

    def start_timer(self):
        try:
            h = int(self.hours_var.get())
            m = int(self.minutes_var.get())
            s = int(self.seconds_var.get())
            total = h * 3600 + m * 60 + s
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的數字")
            return

        if total <= 0:
            messagebox.showwarning("提示", "請設定大於 0 的時間")
            return

        self.total_seconds = total
        self.remaining_seconds = total
        self.running = True
        self.update_controls(running=True)
        
        self.timer_thread = threading.Thread(target=self._run_countdown, daemon=True)
        self.timer_thread.start()

    def stop_timer(self):
        self.running = False
        self.update_controls(running=False)

    def reset_timer(self):
        self.stop_timer()
        self.hours_var.set("00")
        self.minutes_var.set("00")
        self.seconds_var.set("00")
        self.progress.set(0)
        self.status_label.configure(text="準備就緒")

    def update_controls(self, running):
        if running:
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
        else:
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")

    def _run_countdown(self):
        while self.running and self.remaining_seconds > 0:
            time.sleep(1)
            if not self.running:
                break
            self.remaining_seconds -= 1
            
            # Update UI (thread safe call needed normally, but CTk handles some)
            self.window.after(0, self._update_ui_progress)

        if self.remaining_seconds <= 0 and self.running:
            self.running = False
            self.window.after(0, self._timer_finished)

    def _update_ui_progress(self):
        try:
            # Update timer display
            m, s = divmod(self.remaining_seconds, 60)
            h, m = divmod(m, 60)
            self.hours_var.set(f"{h:02d}")
            self.minutes_var.set(f"{m:02d}")
            self.seconds_var.set(f"{s:02d}")
            
            # Update progress bar
            progress = 1 - (self.remaining_seconds / self.total_seconds)
            self.progress.set(progress)
            self.status_label.configure(text=f"剩餘: {h:02d}:{m:02d}:{s:02d}")
        except:
            pass

    def _timer_finished(self):
        self.update_controls(running=False)
        self.progress.set(1)
        self.status_label.configure(text="時間到！")
        
        # Notify
        if self.on_timer_complete:
            self.on_timer_complete(self.title_var.get())
        
        # Bring window to front
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

    def _on_close(self):
        self.running = False
        self.window.destroy()
        self.window = None
