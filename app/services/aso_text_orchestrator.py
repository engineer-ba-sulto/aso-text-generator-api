"""
ASOテキスト生成オーケストレーター
統合APIエンドポイントで使用する統一された処理フローを管理
"""

import asyncio
import logging
import time
from typing import List, Dict, Any
from fastapi import UploadFile

from app.services.csv_analyzer import CSVAnalyzer
from app.services.keyword_selector import KeywordSelector
from app.services.keyword_field_generator import KeywordFieldGenerator
from app.services.title_generator import TitleGenerator
from app.services.subtitle_generator import SubtitleGenerator
from app.services.description_generator import DescriptionGenerator
from app.services.whats_new_generator import WhatsNewGenerator
from app.services.gemini_generator import GeminiGenerator
from app.models.response_models import ASOTextGenerationResponse
from app.utils.exceptions import ASOTextGenerationError
from app.utils.language_validator import LanguageValidator
from app.utils.flow_logger import FlowLogger

logger = logging.getLogger(__name__)


class ASOTextOrchestrator:
    """
    ASOテキスト生成の処理フローを統括するオーケストレーター
    """
    
    def __init__(self):
        self.csv_analyzer = CSVAnalyzer()
        self.keyword_selector = KeywordSelector()
        self.keyword_field_generator = KeywordFieldGenerator()
        self.title_generator = TitleGenerator()
        
        # GeminiGeneratorの初期化
        gemini_generator = GeminiGenerator()
        self.subtitle_generator = SubtitleGenerator(gemini_generator)
        self.description_generator = DescriptionGenerator(gemini_generator)
        
        self.whats_new_generator = WhatsNewGenerator()
        self.flow_logger = FlowLogger()
    
    async def generate_all_texts(
        self,
        csv_file: UploadFile,
        app_name: str,
        features: List[str],
        language: str
    ) -> ASOTextGenerationResponse:
        """
        全ASOテキスト項目を生成する統合処理フロー
        
        Args:
            csv_file: キーワードCSVファイル
            app_name: アプリ名
            features: アプリの特徴リスト
            language: 生成言語 (ja/en)
            
        Returns:
            ASOTextGenerationResponse: 生成された全テキスト項目
            
        Raises:
            ASOTextGenerationError: テキスト生成中のエラー
        """
        try:
            # 言語パラメータの検証
            validated_language = LanguageValidator.validate_language(language)
            
            # 処理フロー開始のログ
            self.flow_logger.log_flow_start(validated_language, app_name)
            
            # ステップ1: CSV分析とキーワード選定
            step_start = time.time()
            keywords_data = await self._analyze_csv_and_select_keywords(csv_file)
            primary_keyword = keywords_data['primary_keyword']
            step_duration = time.time() - step_start
            self.flow_logger.log_step_completion("CSV Analysis & Keyword Selection", step_duration)
            
            # ステップ2: 並列でテキスト生成（パフォーマンス向上）
            step_start = time.time()
            text_results = await self._generate_texts_parallel(
                keywords_data['keywords_data'], primary_keyword, app_name, features, validated_language
            )
            step_duration = time.time() - step_start
            self.flow_logger.log_step_completion("Parallel Text Generation", step_duration)
            
            # ステップ3: レスポンスの構築
            step_start = time.time()
            response = ASOTextGenerationResponse(
                keyword_field=text_results['keyword_field'],
                title=text_results['title'],
                subtitle=text_results['subtitle'],
                description=text_results['description'],
                whats_new=text_results['whats_new'],
                language=validated_language
            )
            step_duration = time.time() - step_start
            self.flow_logger.log_step_completion("Response Construction", step_duration)
            
            # 処理フロー完了のログ
            total_duration = time.time() - self.flow_logger.start_time
            self.flow_logger.log_flow_completion(total_duration)
            
            return response
            
        except Exception as e:
            self.flow_logger.log_error("ASO Text Generation", e)
            raise ASOTextGenerationError(f"テキスト生成中にエラーが発生しました: {str(e)}")
    
    async def _analyze_csv_and_select_keywords(self, csv_file: UploadFile) -> Dict[str, Any]:
        """
        CSV分析と主要キーワード選定を実行
        
        Args:
            csv_file: キーワードCSVファイル
            
        Returns:
            Dict[str, Any]: 分析結果と主要キーワード
        """
        # CSV分析
        keywords_data = await self.csv_analyzer.analyze_csv(csv_file)
        
        # 主要キーワード選定
        primary_keyword = self.keyword_selector.select_primary_keyword(keywords_data)
        
        return {
            'keywords_data': keywords_data,
            'primary_keyword': primary_keyword
        }
    
    async def _generate_texts_parallel(
        self,
        keywords_data: Dict[str, Any],
        primary_keyword: str,
        app_name: str,
        features: List[str],
        language: str
    ) -> Dict[str, str]:
        """
        テキスト生成を並列実行（パフォーマンス向上）
        
        Args:
            keywords_data: キーワード分析データ
            primary_keyword: 主要キーワード
            app_name: アプリ名
            features: アプリの特徴リスト
            language: 生成言語
            
        Returns:
            Dict[str, str]: 生成された各テキスト項目
        """
        # 並列実行するタスクを定義
        tasks = [
            # キーワードフィールド生成
            self._run_async_task(
                self.keyword_field_generator.generate,
                keywords_data, primary_keyword, language
            ),
            # タイトル生成
            self._run_async_task(
                self.title_generator.generate,
                primary_keyword, app_name, language
            ),
            # サブタイトル生成
            self._run_async_task(
                self.subtitle_generator.generate,
                primary_keyword, features, language
            ),
            # 概要生成
            self._run_async_task(
                self.description_generator.generate,
                primary_keyword, features, language
            ),
            # 最新情報生成
            self._run_async_task(
                self.whats_new_generator.generate,
                features, language
            )
        ]
        
        # 並列実行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 結果の検証とエラーハンドリング
        if any(isinstance(result, Exception) for result in results):
            error_messages = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    task_names = ['keyword_field', 'title', 'subtitle', 'description', 'whats_new']
                    error_messages.append(f"{task_names[i]}: {str(result)}")
                    self.flow_logger.log_error(task_names[i], result)
            raise ASOTextGenerationError(f"一部のテキスト生成でエラーが発生しました: {'; '.join(error_messages)}")
        
        return {
            'keyword_field': results[0],
            'title': results[1],
            'subtitle': results[2],
            'description': results[3],
            'whats_new': results[4]
        }
    
    async def _run_async_task(self, func, *args, **kwargs):
        """
        非同期タスクを実行するヘルパーメソッド
        
        Args:
            func: 実行する関数
            *args: 位置引数
            **kwargs: キーワード引数
            
        Returns:
            関数の実行結果
        """
        # 関数が非同期の場合はそのまま実行、そうでなければ同期実行
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            # 同期関数を非同期で実行
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
