"""AI 助理主控制器 - 管理多 AI 協作流程"""
from typing import List, Optional, Callable
from ai_agent import AIAgent
from rag_system import RAGSystem
from meeting_manager import MeetingManager
from logger import logger


class AIAssistant:
    """AI 助理主控制器類別"""

    def __init__(
        self,
        base_url: str = "http://localhost:11434/v1",
        api_key: str = "ollama",
        model: str = "llama3:8b",
        max_rounds: int = 3,
        use_sample_data: bool = False
    ):
        """初始化 AI 助理

        Args:
            base_url: LLM API 基礎 URL
            api_key: API 金鑰
            model: 模型名稱
            max_rounds: 最大討論輪數
            use_sample_data: 是否使用範例資料（測試用）
        """
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.max_rounds = max_rounds

        # 初始化 RAG 系統
        self.rag = RAGSystem()

        if use_sample_data:
            self.rag.populate_sample_data()
            logger.info("已填充 RAG 範例資料")

        # 建立 AI 代理團隊
        self.agents = []
        for role_key in ["creative", "analyst", "pragmatist", "critic", "optimizer"]:
            agent = AIAgent(
                role_key=role_key,
                base_url=base_url,
                api_key=api_key,
                model=model
            )
            self.agents.append(agent)

        logger.info(f"AI 助理已初始化，共 {len(self.agents)} 個代理")

    def process_question(
        self,
        question: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> dict:
        """處理使用者問題，進行 AI 團隊討論

        Args:
            question: 使用者問題
            progress_callback: 進度回調函數

        Returns:
            dict: {
                "question": str,
                "context": str,
                "proposal": str,
                "transcript": list,
                "leader": str,
                "vote_result": dict
            }
        """
        logger.info(f"開始處理問題: {question[:50]}...")

        # Step 1: RAG 檢索背景資料
        if progress_callback:
            progress_callback("正在檢索相關背景資料...")

        context = self.rag.get_context_for_question(question)
        logger.info(f"RAG 檢索完成，背景資料長度: {len(context)}")

        # Step 2: 組合初始提示
        initial_prompt = f"""# 使用者問題
{question}

{context}

請根據你的角色，提供你的觀點和建議。
"""

        # Step 3: 建立會議管理器
        meeting = MeetingManager(
            agents=self.agents,
            max_rounds=self.max_rounds
        )

        # Step 4: 進行討論
        discussion_context = meeting.conduct_discussion(
            initial_prompt=initial_prompt,
            progress_callback=progress_callback
        )

        # Step 5: 進行投票
        vote_result = meeting.conduct_vote(
            context=discussion_context,
            progress_callback=progress_callback
        )

        # Step 6: 提名負責人
        leader = meeting.nominate_leader(
            context=discussion_context,
            progress_callback=progress_callback
        )

        # Step 7: 產出最終提案
        proposal = meeting.generate_final_proposal(
            leader_name=leader,
            context=discussion_context,
            progress_callback=progress_callback
        )

        # Step 8: 取得完整會議記錄
        transcript = meeting.get_full_transcript()

        result = {
            "question": question,
            "context": context,
            "proposal": proposal,
            "transcript": transcript,
            "leader": leader,
            "vote_result": vote_result
        }

        logger.info("問題處理完成")

        if progress_callback:
            progress_callback("完成！")

        return result

    def add_user_data(self, text: str, metadata: dict = None):
        """新增使用者個人化資料

        Args:
            text: 資料內容
            metadata: 元數據（可選）
        """
        self.rag.add_document(text, metadata)
        logger.info("使用者資料已新增到 RAG 系統")

    def get_data_count(self) -> int:
        """取得資料庫中的資料數量

        Returns:
            int: 資料數量
        """
        return self.rag.get_collection_count()

    def clear_all_data(self):
        """清空所有個人化資料"""
        self.rag.clear_all_data()
        logger.info("所有個人化資料已清空")

    def get_agent_names(self) -> List[str]:
        """取得所有代理的名稱

        Returns:
            list: 代理名稱列表
        """
        return [agent.get_role_name() for agent in self.agents]
