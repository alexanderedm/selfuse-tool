"""AI 助理視窗模組 - 多 AI 協作系統 UI"""
import customtkinter as ctk
import threading
from ai_assistant import AIAssistant
from logger import logger


class AIAssistantWindow:
    """AI 助理視窗類別"""

    def __init__(self, tk_root=None):
        """初始化 AI 助理視窗

        Args:
            tk_root: Tkinter 根視窗（可選）
        """
        self.tk_root = tk_root
        self.window = None
        self.assistant = None

        # UI 元件
        self.question_entry = None
        self.progress_label = None
        self.submit_button = None
        self.proposal_textbox = None
        self.transcript_textbox = None
        self.leader_label = None
        self.vote_label = None

        # 顏色主題
        self.bg_color = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.text_color = "#e0e0e0"
        self.text_secondary = "#a0a0a0"
        self.accent_color = "#0078d4"

    def show(self):
        """顯示 AI 助理視窗"""
        if self.window is not None:
            try:
                self.window.lift()
                self.window.focus_force()
                return
            except Exception:
                self.window = None

        # 建立視窗
        if self.tk_root:
            self.window = ctk.CTkToplevel(self.tk_root)
            self.window.transient(self.tk_root)
        else:
            self.window = ctk.CTk()

        self.window.title("🤖 AI 助理 - 多 AI 協作系統")
        self.window.geometry("1000x800")

        # 自動置頂並聚焦
        self.window.lift()
        self.window.focus_force()

        # 建立主框架（可滾動）
        main_frame = ctk.CTkScrollableFrame(
            self.window,
            fg_color="transparent",
            corner_radius=0
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 標題
        title_label = ctk.CTkLabel(
            main_frame,
            text="🤖 AI 團隊協作助理",
            font=("Microsoft JhengHei UI", 20, "bold"),
            text_color=self.accent_color
        )
        title_label.pack(pady=(0, 10))

        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="讓多個 AI 代理平等協作，為您的問題提供全面的解決方案",
            font=("Microsoft JhengHei UI", 10),
            text_color=self.text_secondary
        )
        subtitle_label.pack(pady=(0, 20))

        # 問題輸入區
        self._create_question_section(main_frame)

        # 進度顯示區
        self._create_progress_section(main_frame)

        # 結果顯示區
        self._create_results_section(main_frame)

        # 會議記錄區
        self._create_transcript_section(main_frame)

        # 初始化 AI 助理
        self._init_assistant()

        # 關閉事件
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

        logger.info("AI 助理視窗已開啟")

    def _create_question_section(self, parent):
        """建立問題輸入區

        Args:
            parent: 父框架
        """
        question_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=self.card_bg)
        question_frame.pack(fill="x", pady=(0, 15))

        question_inner = ctk.CTkFrame(question_frame, fg_color="transparent")
        question_inner.pack(padx=20, pady=20, fill="both")

        # 標題
        ctk.CTkLabel(
            question_inner,
            text="💭 您的問題",
            font=("Microsoft JhengHei UI", 12, "bold"),
            text_color=self.text_color,
            anchor="w"
        ).pack(fill="x", pady=(0, 10))

        # 輸入框
        self.question_entry = ctk.CTkTextbox(
            question_inner,
            height=100,
            corner_radius=8,
            font=("Microsoft JhengHei UI", 11)
        )
        self.question_entry.pack(fill="x", pady=(0, 10))

        # 提交按鈕
        self.submit_button = ctk.CTkButton(
            question_inner,
            text="🚀 開始討論",
            command=self._on_submit,
            height=40,
            corner_radius=10,
            font=("Microsoft JhengHei UI", 11, "bold")
        )
        self.submit_button.pack()

    def _create_progress_section(self, parent):
        """建立進度顯示區

        Args:
            parent: 父框架
        """
        progress_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=self.card_bg)
        progress_frame.pack(fill="x", pady=(0, 15))

        progress_inner = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_inner.pack(padx=20, pady=20, fill="both")

        # 進度標籤
        self.progress_label = ctk.CTkLabel(
            progress_inner,
            text="等待開始...",
            font=("Microsoft JhengHei UI", 10),
            text_color=self.text_secondary,
            anchor="w"
        )
        self.progress_label.pack(fill="x")

    def _create_results_section(self, parent):
        """建立結果顯示區

        Args:
            parent: 父框架
        """
        results_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=self.card_bg)
        results_frame.pack(fill="both", expand=True, pady=(0, 15))

        results_inner = ctk.CTkFrame(results_frame, fg_color="transparent")
        results_inner.pack(padx=20, pady=20, fill="both", expand=True)

        # 標題
        ctk.CTkLabel(
            results_inner,
            text="📋 最終提案",
            font=("Microsoft JhengHei UI", 12, "bold"),
            text_color=self.text_color,
            anchor="w"
        ).pack(fill="x", pady=(0, 10))

        # 負責人和投票結果
        info_frame = ctk.CTkFrame(results_inner, fg_color="transparent")
        info_frame.pack(fill="x", pady=(0, 10))

        self.leader_label = ctk.CTkLabel(
            info_frame,
            text="負責人：-",
            font=("Microsoft JhengHei UI", 9),
            text_color=self.text_secondary,
            anchor="w"
        )
        self.leader_label.pack(side="left", padx=(0, 20))

        self.vote_label = ctk.CTkLabel(
            info_frame,
            text="投票：-",
            font=("Microsoft JhengHei UI", 9),
            text_color=self.text_secondary,
            anchor="w"
        )
        self.vote_label.pack(side="left")

        # 提案文字框
        self.proposal_textbox = ctk.CTkTextbox(
            results_inner,
            height=250,
            corner_radius=8,
            font=("Microsoft JhengHei UI", 10),
            wrap="word"
        )
        self.proposal_textbox.pack(fill="both", expand=True)

    def _create_transcript_section(self, parent):
        """建立會議記錄區

        Args:
            parent: 父框架
        """
        transcript_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=self.card_bg)
        transcript_frame.pack(fill="both", expand=True)

        transcript_inner = ctk.CTkFrame(transcript_frame, fg_color="transparent")
        transcript_inner.pack(padx=20, pady=20, fill="both", expand=True)

        # 標題
        ctk.CTkLabel(
            transcript_inner,
            text="📝 完整會議記錄",
            font=("Microsoft JhengHei UI", 12, "bold"),
            text_color=self.text_color,
            anchor="w"
        ).pack(fill="x", pady=(0, 10))

        # 會議記錄文字框
        self.transcript_textbox = ctk.CTkTextbox(
            transcript_inner,
            height=250,
            corner_radius=8,
            font=("Microsoft JhengHei UI", 9),
            wrap="word"
        )
        self.transcript_textbox.pack(fill="both", expand=True)

    def _init_assistant(self):
        """初始化 AI 助理"""
        try:
            self.assistant = AIAssistant(use_sample_data=True)
            logger.info("AI 助理已初始化")
            self._update_progress("AI 團隊已就緒，等待您的問題...")
        except Exception as e:
            logger.error(f"初始化 AI 助理時發生錯誤: {e}")
            self._update_progress(f"錯誤：{e}")

    def _update_progress(self, message: str):
        """更新進度訊息

        Args:
            message: 進度訊息
        """
        if self.progress_label:
            self.progress_label.configure(text=message)

    def _update_results(self, result: dict):
        """更新結果顯示

        Args:
            result: 結果字典
        """
        # 更新負責人
        if self.leader_label:
            self.leader_label.configure(text=f"負責人：{result['leader']}")

        # 更新投票結果
        if self.vote_label:
            vote_result = result['vote_result']
            self.vote_label.configure(
                text=f"投票：{vote_result['agree_count']}/{vote_result['total_count']} 同意"
            )

        # 更新提案
        if self.proposal_textbox:
            self.proposal_textbox.delete("0.0", "end")
            self.proposal_textbox.insert("0.0", result['proposal'])

        # 更新會議記錄
        if self.transcript_textbox:
            self.transcript_textbox.delete("0.0", "end")
            transcript_text = ""
            for entry in result['transcript']:
                transcript_text += f"[第 {entry['round']} 輪] {entry['speaker']}:\n"
                transcript_text += f"{entry['content']}\n\n"
            self.transcript_textbox.insert("0.0", transcript_text)

    def _on_submit(self):
        """處理提交按鈕點擊"""
        question = self.question_entry.get("0.0", "end").strip()

        if not question:
            self._update_progress("請輸入問題！")
            return

        # 停用提交按鈕
        if self.submit_button:
            self.submit_button.configure(state="disabled", text="處理中...")

        # 在新執行緒中處理問題
        thread = threading.Thread(target=self._process_question, args=(question,), daemon=True)
        thread.start()

    def _process_question(self, question: str):
        """處理使用者問題（在背景執行緒）

        Args:
            question: 使用者問題
        """
        try:
            result = self.assistant.process_question(
                question=question,
                progress_callback=self._update_progress
            )

            # 在主執行緒更新 UI
            if self.window:
                self.window.after(0, self._update_results, result)
                self.window.after(0, self._update_progress, "完成！")
                if self.submit_button:
                    self.window.after(0, lambda: self.submit_button.configure(
                        state="normal", text="🚀 開始討論"
                    ))

        except Exception as e:
            logger.error(f"處理問題時發生錯誤: {e}")
            if self.window:
                self.window.after(0, self._update_progress, f"錯誤：{e}")
                if self.submit_button:
                    self.window.after(0, lambda: self.submit_button.configure(
                        state="normal", text="🚀 開始討論"
                    ))

    def _close_window(self):
        """關閉視窗"""
        if self.window:
            self.window.destroy()
            self.window = None
        logger.info("AI 助理視窗已關閉")
