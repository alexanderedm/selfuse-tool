"""AI 代理模組 - 代表單一 AI 角色"""
import openai
from typing import Dict, List, Optional
from logger import logger


class AIAgent:
    """AI 代理類別 - 代表一個 AI 角色"""

    # 預定義角色
    ROLES = {
        "creative": {
            "name": "創意家",
            "prompt": "你是一位富有創造力的思考者，專注於提出創新且有趣的想法。"
        },
        "analyst": {
            "name": "風險分析師",
            "prompt": "你是一位謹慎的風險分析師，專注於識別潛在問題和風險。"
        },
        "pragmatist": {
            "name": "務實主義者",
            "prompt": "你是一位務實的執行者，專注於可行性和實際操作。"
        },
        "critic": {
            "name": "批判思考者",
            "prompt": "你是一位建設性的批評者，專注於找出邏輯漏洞和改進空間。"
        },
        "optimizer": {
            "name": "優化專家",
            "prompt": "你是一位效率專家，專注於優化流程和提升效能。"
        }
    }

    def __init__(
        self,
        role_key: str,
        base_url: str = "http://localhost:11434/v1",
        api_key: str = "ollama",
        model: str = "llama3:8b",
        agent_id: Optional[int] = None
    ):
        """初始化 AI 代理

        Args:
            role_key: 角色鍵值（creative, analyst, pragmatist, critic, optimizer）
            base_url: API 基礎 URL（預設 Ollama 本地）
            api_key: API 金鑰（本地 LLM 可隨意填）
            model: 模型名稱
            agent_id: 代理 ID（可選）
        """
        if role_key not in self.ROLES:
            raise ValueError(f"無效的角色鍵值: {role_key}")

        self.role_key = role_key
        self.role_info = self.ROLES[role_key]
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.agent_id = agent_id or id(self)

        # 建立 OpenAI 客戶端（連接本地 LLM）
        self.client = openai.OpenAI(
            base_url=base_url,
            api_key=api_key
        )

        logger.info(f"AI 代理已初始化：{self.role_info['name']} (ID: {self.agent_id})")

    def get_response(
        self,
        prompt: str,
        context: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7
    ) -> str:
        """取得 AI 回應

        Args:
            prompt: 提示詞
            context: 對話上下文（訊息列表）
            temperature: 溫度參數（控制創造性）

        Returns:
            str: AI 的回應文字
        """
        try:
            # 建立訊息列表
            messages = [
                {"role": "system", "content": self.role_info['prompt']}
            ]

            # 加入上下文
            if context:
                messages.extend(context)

            # 加入當前提示
            messages.append({"role": "user", "content": prompt})

            logger.debug(f"[{self.role_info['name']}] 發送請求到 LLM")

            # 呼叫 API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )

            # 提取回應文字
            reply = response.choices[0].message.content.strip()

            logger.info(f"[{self.role_info['name']}] 收到回應，長度: {len(reply)}")

            return reply

        except Exception as e:
            logger.error(f"[{self.role_info['name']}] 取得回應時發生錯誤: {e}")
            return f"[錯誤] 無法取得 {self.role_info['name']} 的回應"

    def vote(
        self,
        question: str,
        context: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, any]:
        """投票：是否同意結束討論

        Args:
            question: 投票問題
            context: 對話上下文

        Returns:
            dict: {"vote": "同意/不同意", "reason": "理由"}
        """
        prompt = f"""{question}

請以以下格式回答：
[投票]: 同意 或 不同意
[理由]: 你的判斷理由（一句話說明）
"""

        response = self.get_response(prompt, context, temperature=0.3)

        # 解析回應
        vote = "不同意"  # 預設
        reason = "無法解析回應"

        lines = response.strip().split('\n')
        for line in lines:
            if line.startswith('[投票]'):
                vote_text = line.replace('[投票]:', '').strip()
                if '同意' in vote_text:
                    vote = "同意"
                elif '不同意' in vote_text:
                    vote = "不同意"
            elif line.startswith('[理由]'):
                reason = line.replace('[理由]:', '').strip()

        logger.info(f"[{self.role_info['name']}] 投票: {vote}, 理由: {reason}")

        return {
            "agent_id": self.agent_id,
            "agent_name": self.role_info['name'],
            "vote": vote,
            "reason": reason
        }

    def nominate(
        self,
        question: str,
        candidates: List[str],
        context: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """提名：選擇最適合的負責人

        Args:
            question: 提名問題
            candidates: 候選人列表
            context: 對話上下文

        Returns:
            str: 被提名者的名稱
        """
        candidates_str = "、".join(candidates)
        prompt = f"""{question}

候選人：{candidates_str}

請直接回答候選人的名稱（例如：創意家）
"""

        response = self.get_response(prompt, context, temperature=0.3)

        # 找出候選人名稱
        for candidate in candidates:
            if candidate in response:
                logger.info(f"[{self.role_info['name']}] 提名: {candidate}")
                return candidate

        # 如果沒找到，回傳第一個候選人
        logger.warning(f"[{self.role_info['name']}] 無法解析提名，預設提名第一個候選人")
        return candidates[0] if candidates else ""

    def get_role_name(self) -> str:
        """取得角色名稱"""
        return self.role_info['name']

    def __repr__(self) -> str:
        return f"AIAgent(role={self.role_info['name']}, model={self.model})"
