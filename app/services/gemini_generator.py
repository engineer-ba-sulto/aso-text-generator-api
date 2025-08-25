"""
Gemini API連携サービス
Google Gemini APIとの連携を行うサービス
"""

import os
import time
from typing import Any, Dict, List, Optional

import google.genai as genai
from loguru import logger

from app.config import settings


class GeminiGenerator:
    """Gemini API連携クラス"""

    def __init__(self, api_key: str = None, model_name: str = None):
        """
        初期化

        Args:
            api_key: Gemini APIキー
            model_name: 使用するモデル名（指定しない場合は設定ファイルから取得）
        """
        self.api_key = api_key or settings.gemini_api_key or settings.google_api_key
        if not self.api_key:
            raise ValueError("Gemini API key is required")

        # モデル名の検証と設定
        self.model_name = model_name or settings.gemini_model
        self._validate_model(self.model_name)

        # Gemini API設定
        self.client = genai.Client(api_key=self.api_key)
        self.timeout = settings.gemini_timeout
        self.max_retries = settings.gemini_max_retries

    def _validate_model(self, model_name: str) -> None:
        """
        モデル名の検証

        Args:
            model_name: 検証するモデル名

        Raises:
            ValueError: 非推奨モデルまたは無効なモデルが指定された場合
        """
        if not settings.is_valid_model(model_name):
            category = settings.get_model_category(model_name)
            if category == "deprecated":
                raise ValueError(
                    f"非推奨モデル '{model_name}' は使用できません。"
                    f"推奨モデル: {settings.RECOMMENDED_MODELS}, "
                    f"許容モデル: {settings.ACCEPTABLE_MODELS}"
                )
            else:
                raise ValueError(
                    f"無効なモデル '{model_name}' が指定されました。"
                    f"利用可能なモデル: {settings.available_models}"
                )

        logger.info(
            f"使用モデル: {model_name} (カテゴリ: {settings.get_model_category(model_name)})"
        )

    def generate_subtitle(self, prompt: str, language: str = "ja") -> str:
        """
        サブタイトル生成（30文字制限）

        Args:
            prompt: プロンプト文字列
            language: 言語（ja/en）

        Returns:
            生成されたサブタイトル
        """
        try:
            response = self._call_gemini_api(prompt, max_tokens=50)
            subtitle = self._validate_text_length(response, 30)
            logger.info(f"Generated subtitle: {subtitle}")
            return subtitle
        except Exception as e:
            logger.error(f"Error generating subtitle: {e}")
            raise

    def generate_description(self, prompt: str, language: str = "ja") -> str:
        """
        概要生成（4000文字制限）

        Args:
            prompt: プロンプト文字列
            language: 言語（ja/en）

        Returns:
            生成された概要
        """
        try:
            response = self._call_gemini_api(prompt, max_tokens=2000)
            description = self._validate_text_length(response, 4000)
            logger.info(f"Generated description: {len(description)} characters")
            return description
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            raise

    def _call_gemini_api(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Gemini APIを呼び出す

        Args:
            prompt: プロンプト文字列
            max_tokens: 最大トークン数

        Returns:
            API応答テキスト
        """

        def api_call():
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40,
                ),
            )
            return response.text

        return self._retry_with_backoff(api_call)

    def _retry_with_backoff(self, func, max_retries: int = 3) -> Any:
        """
        バックオフ付きリトライ機能

        Args:
            func: 実行する関数
            max_retries: 最大リトライ回数

        Returns:
            関数の実行結果
        """
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Max retries reached: {e}")
                    raise

                wait_time = 2**attempt  # 1秒、2秒、4秒
                logger.warning(f"API call failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)

    def _validate_text_length(self, text: str, max_length: int) -> str:
        """
        テキスト長の検証と調整

        Args:
            text: 検証対象テキスト
            max_length: 最大文字数

        Returns:
            調整されたテキスト
        """
        if len(text) <= max_length:
            return text

        # 文字数制限を超える場合は切り詰める
        truncated = text[:max_length]
        # 文の途中で切れないように調整
        last_period = truncated.rfind("。")
        if (
            last_period > 0 and last_period > max_length * 0.5
        ):  # 50%以上が完了している場合
            return truncated[: last_period + 1]

        return truncated

    def analyze_keywords(self, text: str) -> List[str]:
        """
        テキストからキーワードを分析する

        Args:
            text: 分析対象のテキスト

        Returns:
            抽出されたキーワードのリスト
        """
        prompt = f"以下のテキストから重要なキーワードを抽出してください（カンマ区切りで返してください）:\n\n{text}"
        try:
            response = self._call_gemini_api(prompt, max_tokens=200)
            keywords = [kw.strip() for kw in response.split(",")]
            return keywords
        except Exception as e:
            logger.error(f"Error analyzing keywords: {e}")
            return []

    def optimize_text(self, text: str, target_length: int = 100) -> str:
        """
        テキストを最適化する

        Args:
            text: 最適化対象のテキスト
            target_length: 目標文字数

        Returns:
            最適化されたテキスト
        """
        prompt = (
            f"以下のテキストを{target_length}文字程度に最適化してください:\n\n{text}"
        )
        try:
            response = self._call_gemini_api(prompt, max_tokens=500)
            return self._validate_text_length(response, target_length)
        except Exception as e:
            logger.error(f"Error optimizing text: {e}")
            return text
