"""會議管理器模組 - 管理 AI 討論流程"""
from typing import List, Dict, Optional, Callable
from ai_agent import AIAgent
from logger import logger


class MeetingManager:
    """會議管理器類別 - 協調 AI 團隊討論"""

    def __init__(
        self,
        agents: List[AIAgent],
        max_rounds: int = 3,
        vote_threshold: float = 0.5,
        context_limit: int = 4000
    ):
        """初始化會議管理器

        Args:
            agents: AI 代理列表
            max_rounds: 最大討論輪數
            vote_threshold: 投票門檻（0.5 = 超過半數）
            context_limit: 上下文字數限制
        """
        self.agents = agents
        self.max_rounds = max_rounds
        self.vote_threshold = vote_threshold
        self.context_limit = context_limit

        # 會議記錄
        self.transcript = []
        self.current_round = 0

        logger.info(f"會議管理器已初始化，{len(agents)} 個代理，最多 {max_rounds} 輪討論")

    def add_to_transcript(self, speaker: str, content: str, round_num: int = None):
        """新增發言到會議記錄

        Args:
            speaker: 發言者名稱
            content: 發言內容
            round_num: 輪次編號（可選）
        """
        entry = {
            "round": round_num or self.current_round,
            "speaker": speaker,
            "content": content
        }
        self.transcript.append(entry)
        logger.debug(f"[第 {entry['round']} 輪] {speaker}: {content[:50]}...")

    def get_transcript_text(self, max_chars: Optional[int] = None) -> str:
        """取得會議記錄文字

        Args:
            max_chars: 最大字數限制（可選）

        Returns:
            str: 格式化的會議記錄
        """
        lines = []
        for entry in self.transcript:
            lines.append(f"[第 {entry['round']} 輪] {entry['speaker']}:\n{entry['content']}\n")

        full_text = "\n".join(lines)

        # 如果超過字數限制，進行摘要
        if max_chars and len(full_text) > max_chars:
            logger.warning(f"會議記錄超過限制 ({len(full_text)} > {max_chars})，進行摘要")
            return self._summarize_transcript(full_text, max_chars)

        return full_text

    def _summarize_transcript(self, text: str, max_chars: int) -> str:
        """摘要會議記錄（簡化版）

        Args:
            text: 原始會議記錄
            max_chars: 最大字數

        Returns:
            str: 摘要後的文字
        """
        # 簡單的摘要：保留最近的內容
        if len(text) <= max_chars:
            return text

        # 計算需要保留的輪次
        lines = text.split('\n')
        total_chars = 0
        keep_lines = []

        for line in reversed(lines):
            if total_chars + len(line) > max_chars:
                break
            keep_lines.insert(0, line)
            total_chars += len(line)

        summary = "\n".join(keep_lines)
        summary = f"[前面的討論已摘要]\n\n{summary}"

        logger.info(f"會議記錄已摘要：{len(text)} -> {len(summary)} 字元")

        return summary

    def conduct_discussion(
        self,
        initial_prompt: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> List[Dict[str, str]]:
        """進行討論輪次

        Args:
            initial_prompt: 初始提示（問題 + 背景資料）
            progress_callback: 進度回調函數

        Returns:
            list: 會議記錄（上下文格式）
        """
        logger.info("開始 AI 團隊討論")

        # 初始化上下文
        context = [{"role": "user", "content": initial_prompt}]

        for round_num in range(1, self.max_rounds + 1):
            self.current_round = round_num
            logger.info(f"===== 第 {round_num} 輪討論 =====")

            if progress_callback:
                progress_callback(f"進行第 {round_num} 輪討論...")

            # 取得當前會議記錄
            transcript_text = self.get_transcript_text(self.context_limit)

            # 每個代理依序發言
            for agent in self.agents:
                prompt = f"""以下是目前的討論記錄：

{transcript_text}

請根據你的角色（{agent.get_role_name()}）提出你的看法或建議。
"""

                response = agent.get_response(prompt, context)

                # 記錄發言
                self.add_to_transcript(agent.get_role_name(), response, round_num)

                # 更新上下文
                context.append({"role": "assistant", "content": f"[{agent.get_role_name()}]: {response}"})

        logger.info("討論輪次完成")

        return context

    def conduct_vote(
        self,
        context: List[Dict[str, str]],
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, any]:
        """進行共識投票

        Args:
            context: 對話上下文
            progress_callback: 進度回調函數

        Returns:
            dict: {"passed": bool, "votes": list, "agree_count": int, "total_count": int}
        """
        logger.info("開始共識投票")

        if progress_callback:
            progress_callback("正在進行共識投票...")

        transcript_text = self.get_transcript_text(self.context_limit)

        question = f"""根據以下討論記錄，請投票是否可以結束討論並產出最終提案：

{transcript_text}

判斷標準：
- 是否已經充分討論各種觀點？
- 是否已經找到可行的解決方案？
- 是否還有重要的問題未解決？
"""

        votes = []
        agree_count = 0

        for agent in self.agents:
            vote_result = agent.vote(question, context)
            votes.append(vote_result)

            if vote_result['vote'] == "同意":
                agree_count += 1

            logger.info(f"[投票] {vote_result['agent_name']}: {vote_result['vote']} - {vote_result['reason']}")

        total_count = len(self.agents)
        passed = (agree_count / total_count) >= self.vote_threshold

        result = {
            "passed": passed,
            "votes": votes,
            "agree_count": agree_count,
            "total_count": total_count
        }

        logger.info(f"投票結果: {agree_count}/{total_count} 同意，{'通過' if passed else '未通過'}")

        return result

    def nominate_leader(
        self,
        context: List[Dict[str, str]],
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> str:
        """提名並選出負責人

        Args:
            context: 對話上下文
            progress_callback: 進度回調函數

        Returns:
            str: 負責人名稱
        """
        logger.info("開始提名負責人")

        if progress_callback:
            progress_callback("正在提名專案負責人...")

        candidates = [agent.get_role_name() for agent in self.agents]
        question = "根據討論內容，請提名最適合撰寫最終提案的角色。"

        # 每個代理提名
        nominations = {}
        for agent in self.agents:
            nominee = agent.nominate(question, candidates, context)
            nominations[nominee] = nominations.get(nominee, 0) + 1
            logger.info(f"[提名] {agent.get_role_name()} 提名: {nominee}")

        # 找出得票最高者
        leader = max(nominations, key=nominations.get)

        logger.info(f"負責人選出: {leader} ({nominations[leader]} 票)")

        return leader

    def generate_final_proposal(
        self,
        leader_name: str,
        context: List[Dict[str, str]],
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> str:
        """由負責人產出最終提案

        Args:
            leader_name: 負責人名稱
            context: 對話上下文
            progress_callback: 進度回調函數

        Returns:
            str: 最終提案
        """
        logger.info(f"由 {leader_name} 撰寫最終提案")

        if progress_callback:
            progress_callback(f"{leader_name} 正在撰寫最終提案...")

        # 找到負責人代理
        leader = None
        for agent in self.agents:
            if agent.get_role_name() == leader_name:
                leader = agent
                break

        if not leader:
            logger.error(f"找不到負責人: {leader_name}")
            return "[錯誤] 找不到指定的負責人"

        transcript_text = self.get_transcript_text(self.context_limit)

        prompt = f"""你已被選為負責人，請根據以下完整討論記錄，撰寫一份清晰、條理分明的最終提案：

{transcript_text}

最終提案格式：
# 最終提案

## 問題概述
[簡述原始問題]

## 推薦方案
[具體的行動建議]

## 理由與考量
[為什麼選擇這個方案，有哪些考量]

## 注意事項
[需要注意的風險或限制]
"""

        proposal = leader.get_response(prompt, context, temperature=0.5)

        logger.info(f"最終提案已完成，長度: {len(proposal)}")

        return proposal

    def get_full_transcript(self) -> List[Dict[str, any]]:
        """取得完整會議記錄

        Returns:
            list: 會議記錄列表
        """
        return self.transcript

    def clear_transcript(self):
        """清空會議記錄"""
        self.transcript = []
        self.current_round = 0
        logger.info("會議記錄已清空")
