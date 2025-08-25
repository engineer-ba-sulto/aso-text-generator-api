import asyncio
from typing import Dict, Any, Optional
from fastapi import UploadFile
from app.services.csv_analyzer import CSVAnalyzer
from app.services.keyword_selector import KeywordSelector
from app.services.keyword_field_generator import KeywordFieldGenerator
from app.services.title_generator import TitleGenerator
from app.services.subtitle_generator import SubtitleGenerator
from app.services.description_generator import DescriptionGenerator
from app.services.whats_new_generator import WhatsNewGenerator
from app.utils.cache_manager import CacheManager
from app.utils.flow_logger import FlowLogger

class OptimizedIndividualOrchestrator:
    """
    最適化された個別テキスト生成オーケストレーター
    """
    
    def __init__(self):
        self.csv_analyzer = CSVAnalyzer()
        self.keyword_selector = KeywordSelector()
        self.keyword_field_generator = KeywordFieldGenerator()
        self.title_generator = TitleGenerator()
        self.subtitle_generator = SubtitleGenerator()
        self.description_generator = DescriptionGenerator()
        self.whats_new_generator = WhatsNewGenerator()
        self.cache_manager = CacheManager()
        self.flow_logger = FlowLogger()
    
    async def generate_keyword_field_optimized(
        self, 
        csv_file: UploadFile, 
        language: str
    ) -> str:
        """
        最適化されたキーワードフィールド生成
        
        Args:
            csv_file: キーワードCSVファイル
            language: 生成言語
            
        Returns:
            str: 生成されたキーワードフィールド
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # キャッシュキーの生成
            cache_key = self.cache_manager._generate_cache_key(
                'keyword_field', 
                csv_file.filename, 
                language
            )
            
            # キャッシュから取得を試行
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                self.flow_logger.log_step_completion(
                    'keyword_field_cache_hit', 
                    asyncio.get_event_loop().time() - start_time
                )
                return cached_result
            
            # CSV分析とキーワード選定（並列実行可能な部分）
            csv_analysis_task = asyncio.create_task(
                self.csv_analyzer.analyze_csv(csv_file)
            )
            
            # CSV分析完了を待機
            keywords_data = await csv_analysis_task
            
            # キーワード選定
            primary_keyword = self.keyword_selector.select_primary_keyword(keywords_data)
            
            # キーワードフィールド生成
            keyword_field = await self.keyword_field_generator.generate(
                keywords_data, primary_keyword, language
            )
            
            # キャッシュに保存
            await self.cache_manager.set(cache_key, keyword_field)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            self.flow_logger.log_step_completion('keyword_field_generation', processing_time)
            
            return keyword_field
            
        except Exception as e:
            self.flow_logger.log_error('keyword_field_generation', e)
            raise
    
    async def generate_title_optimized(
        self, 
        primary_keyword: str, 
        app_name: str, 
        language: str
    ) -> str:
        """
        最適化されたタイトル生成
        
        Args:
            primary_keyword: 主要キーワード
            app_name: アプリ名
            language: 生成言語
            
        Returns:
            str: 生成されたタイトル
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # キャッシュキーの生成
            cache_key = self.cache_manager._generate_cache_key(
                'title', 
                primary_keyword, 
                app_name, 
                language
            )
            
            # キャッシュから取得を試行
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                self.flow_logger.log_step_completion(
                    'title_cache_hit', 
                    asyncio.get_event_loop().time() - start_time
                )
                return cached_result
            
            # タイトル生成
            title = await self.title_generator.generate(
                primary_keyword, app_name, language
            )
            
            # キャッシュに保存
            await self.cache_manager.set(cache_key, title)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            self.flow_logger.log_step_completion('title_generation', processing_time)
            
            return title
            
        except Exception as e:
            self.flow_logger.log_error('title_generation', e)
            raise
    
    async def generate_subtitle_optimized(
        self, 
        primary_keyword: str, 
        features: list, 
        language: str
    ) -> str:
        """
        最適化されたサブタイトル生成
        
        Args:
            primary_keyword: 主要キーワード
            features: アプリの特徴リスト
            language: 生成言語
            
        Returns:
            str: 生成されたサブタイトル
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # キャッシュキーの生成
            cache_key = self.cache_manager._generate_cache_key(
                'subtitle', 
                primary_keyword, 
                tuple(sorted(features)), 
                language
            )
            
            # キャッシュから取得を試行
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                self.flow_logger.log_step_completion(
                    'subtitle_cache_hit', 
                    asyncio.get_event_loop().time() - start_time
                )
                return cached_result
            
            # サブタイトル生成
            subtitle = await self.subtitle_generator.generate(
                primary_keyword, features, language
            )
            
            # キャッシュに保存
            await self.cache_manager.set(cache_key, subtitle)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            self.flow_logger.log_step_completion('subtitle_generation', processing_time)
            
            return subtitle
            
        except Exception as e:
            self.flow_logger.log_error('subtitle_generation', e)
            raise
    
    async def generate_description_optimized(
        self, 
        primary_keyword: str, 
        features: list, 
        language: str
    ) -> str:
        """
        最適化された概要生成
        
        Args:
            primary_keyword: 主要キーワード
            features: アプリの特徴リスト
            language: 生成言語
            
        Returns:
            str: 生成された概要
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # キャッシュキーの生成
            cache_key = self.cache_manager._generate_cache_key(
                'description', 
                primary_keyword, 
                tuple(sorted(features)), 
                language
            )
            
            # キャッシュから取得を試行
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                self.flow_logger.log_step_completion(
                    'description_cache_hit', 
                    asyncio.get_event_loop().time() - start_time
                )
                return cached_result
            
            # 概要生成
            description = await self.description_generator.generate(
                primary_keyword, features, language
            )
            
            # キャッシュに保存
            await self.cache_manager.set(cache_key, description)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            self.flow_logger.log_step_completion('description_generation', processing_time)
            
            return description
            
        except Exception as e:
            self.flow_logger.log_error('description_generation', e)
            raise
    
    async def generate_whats_new_optimized(
        self, 
        features: list, 
        language: str
    ) -> str:
        """
        最適化された最新情報生成
        
        Args:
            features: アプリの特徴リスト
            language: 生成言語
            
        Returns:
            str: 生成された最新情報
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # キャッシュキーの生成
            cache_key = self.cache_manager._generate_cache_key(
                'whats_new', 
                tuple(sorted(features)), 
                language
            )
            
            # キャッシュから取得を試行
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                self.flow_logger.log_step_completion(
                    'whats_new_cache_hit', 
                    asyncio.get_event_loop().time() - start_time
                )
                return cached_result
            
            # 最新情報生成
            whats_new = await self.whats_new_generator.generate(
                features, language
            )
            
            # キャッシュに保存
            await self.cache_manager.set(cache_key, whats_new)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            self.flow_logger.log_step_completion('whats_new_generation', processing_time)
            
            return whats_new
            
        except Exception as e:
            self.flow_logger.log_error('whats_new_generation', e)
            raise
