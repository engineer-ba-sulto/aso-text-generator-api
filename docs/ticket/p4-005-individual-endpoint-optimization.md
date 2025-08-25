# P4-005: 個別エンドポイントの処理フロー最適化

## 概要

個別APIエンドポイントの処理フローを最適化し、必要な最小限の処理（CSV分析、キーワード選定、該当テキスト生成）のみを実行することで、効率的な処理を実現します。キャッシュ機能、並列処理、リソース管理などの最適化技術を適用します。

## 目標

- 個別エンドポイントの処理効率化
- キャッシュ機能の実装
- リソース使用量の最適化
- レスポンス時間の短縮
- スケーラビリティの向上

## 実装内容

### 1. キャッシュ機能の実装

```python
# app/utils/cache_manager.py
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import json

class CacheManager:
    """
    個別エンドポイント用のキャッシュマネージャー
    """
    
    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl_hours = ttl_hours
        self._lock = asyncio.Lock()
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """
        キャッシュキーを生成
        
        Args:
            *args: 位置引数
            **kwargs: キーワード引数
            
        Returns:
            str: キャッシュキー
        """
        # 引数をJSON文字列に変換
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        
        # SHA256ハッシュを生成
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """
        キャッシュから値を取得
        
        Args:
            key: キャッシュキー
            
        Returns:
            Optional[Any]: キャッシュされた値（存在しない場合はNone）
        """
        async with self._lock:
            if key in self.cache:
                cache_entry = self.cache[key]
                
                # TTLチェック
                if datetime.now() < cache_entry['expires_at']:
                    return cache_entry['value']
                else:
                    # 期限切れの場合は削除
                    del self.cache[key]
            
            return None
    
    async def set(self, key: str, value: Any) -> None:
        """
        キャッシュに値を保存
        
        Args:
            key: キャッシュキー
            value: 保存する値
        """
        async with self._lock:
            # キャッシュサイズ制限チェック
            if len(self.cache) >= self.max_size:
                # 最も古いエントリを削除
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k]['created_at']
                )
                del self.cache[oldest_key]
            
            # 新しいエントリを追加
            self.cache[key] = {
                'value': value,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=self.ttl_hours)
            }
    
    async def invalidate_pattern(self, pattern: str) -> None:
        """
        パターンに一致するキャッシュエントリを削除
        
        Args:
            pattern: 削除するパターン
        """
        async with self._lock:
            keys_to_delete = [
                key for key in self.cache.keys()
                if pattern in key
            ]
            for key in keys_to_delete:
                del self.cache[key]
    
    async def clear(self) -> None:
        """キャッシュをクリア"""
        async with self._lock:
            self.cache.clear()
```

### 2. 最適化された個別オーケストレーター

```python
# app/services/optimized_individual_orchestrator.py
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
```

### 3. リソース管理の最適化

```python
# app/utils/resource_manager.py
import asyncio
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
import psutil
import gc

class ResourceManager:
    """
    リソース使用量を監視・管理するマネージャー
    """
    
    def __init__(self):
        self.memory_threshold = 0.8  # 80%のメモリ使用率で警告
        self.cpu_threshold = 0.9     # 90%のCPU使用率で警告
    
    def get_memory_usage(self) -> float:
        """
        現在のメモリ使用率を取得
        
        Returns:
            float: メモリ使用率（0.0-1.0）
        """
        return psutil.virtual_memory().percent / 100.0
    
    def get_cpu_usage(self) -> float:
        """
        現在のCPU使用率を取得
        
        Returns:
            float: CPU使用率（0.0-1.0）
        """
        return psutil.cpu_percent(interval=0.1) / 100.0
    
    def check_resource_limits(self) -> Dict[str, Any]:
        """
        リソース制限をチェック
        
        Returns:
            Dict[str, Any]: リソース使用状況
        """
        memory_usage = self.get_memory_usage()
        cpu_usage = self.get_cpu_usage()
        
        return {
            'memory_usage': memory_usage,
            'cpu_usage': cpu_usage,
            'memory_warning': memory_usage > self.memory_threshold,
            'cpu_warning': cpu_usage > self.cpu_threshold,
            'overloaded': memory_usage > self.memory_threshold or cpu_usage > self.cpu_threshold
        }
    
    async def optimize_memory(self) -> None:
        """
        メモリ使用量を最適化
        """
        # ガベージコレクションを実行
        gc.collect()
        
        # 少し待機してメモリ解放を待つ
        await asyncio.sleep(0.1)
    
    @asynccontextmanager
    async def resource_monitor(self):
        """
        リソース監視のコンテキストマネージャー
        """
        try:
            yield
        finally:
            # 処理完了後にメモリ最適化を実行
            await self.optimize_memory()
```

### 4. 最適化されたエンドポイントの実装

```python
# app/api/v1/optimized_aso_endpoints.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List
from app.models.request_models import (
    KeywordFieldRequest, TitleRequest, SubtitleRequest, 
    DescriptionRequest, WhatsNewRequest
)
from app.models.response_models import (
    KeywordFieldResponse, TitleResponse, SubtitleResponse,
    DescriptionResponse, WhatsNewResponse
)
from app.services.optimized_individual_orchestrator import OptimizedIndividualOrchestrator
from app.utils.response_builder import ResponseBuilder
from app.utils.resource_manager import ResourceManager
from app.utils.flow_logger import FlowLogger

router = APIRouter()

# 最適化されたキーワードフィールド生成エンドポイント
@router.post("/generate-keyword-field", response_model=KeywordFieldResponse)
async def generate_keyword_field_optimized(
    csv_file: UploadFile = File(...),
    language: str = Form(...),
    orchestrator: OptimizedIndividualOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends(),
    resource_manager: ResourceManager = Depends(),
    flow_logger: FlowLogger = Depends()
):
    """
    最適化されたキーワードフィールド生成エンドポイント
    """
    try:
        # リソース監視開始
        async with resource_manager.resource_monitor():
            # リソース制限チェック
            resource_status = resource_manager.check_resource_limits()
            if resource_status['overloaded']:
                flow_logger.log_error('resource_overload', Exception("Resource overload detected"))
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable due to high resource usage"
                )
            
            # キーワードフィールド生成
            keyword_field = await orchestrator.generate_keyword_field_optimized(
                csv_file, language
            )
            
            # レスポンス構築
            return response_builder.build_keyword_field_response(
                keyword_field=keyword_field,
                language=language
            )
            
    except HTTPException:
        raise
    except Exception as e:
        flow_logger.log_error('keyword_field_generation', e)
        raise HTTPException(
            status_code=500,
            detail=f"キーワードフィールド生成中にエラーが発生しました: {str(e)}"
        )

# 最適化されたタイトル生成エンドポイント
@router.post("/generate-title", response_model=TitleResponse)
async def generate_title_optimized(
    request: TitleRequest,
    orchestrator: OptimizedIndividualOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends(),
    resource_manager: ResourceManager = Depends(),
    flow_logger: FlowLogger = Depends()
):
    """
    最適化されたタイトル生成エンドポイント
    """
    try:
        async with resource_manager.resource_monitor():
            # リソース制限チェック
            resource_status = resource_manager.check_resource_limits()
            if resource_status['overloaded']:
                flow_logger.log_error('resource_overload', Exception("Resource overload detected"))
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable due to high resource usage"
                )
            
            # タイトル生成
            title = await orchestrator.generate_title_optimized(
                request.primary_keyword,
                request.app_name,
                request.language
            )
            
            return response_builder.build_title_response(
                title=title,
                language=request.language
            )
            
    except HTTPException:
        raise
    except Exception as e:
        flow_logger.log_error('title_generation', e)
        raise HTTPException(
            status_code=500,
            detail=f"タイトル生成中にエラーが発生しました: {str(e)}"
        )
```

## 実装手順

1. **キャッシュマネージャーの実装**
   - `app/utils/cache_manager.py`を作成
   - キャッシュ機能を実装

2. **最適化されたオーケストレーターの実装**
   - `app/services/optimized_individual_orchestrator.py`を作成
   - キャッシュ機能を統合した処理フローを実装

3. **リソースマネージャーの実装**
   - `app/utils/resource_manager.py`を作成
   - リソース監視・管理機能を実装

4. **最適化されたエンドポイントの実装**
   - `app/api/v1/optimized_aso_endpoints.py`を作成
   - 最適化機能を統合したエンドポイントを実装

5. **既存エンドポイントの更新**
   - 最適化されたバージョンに置き換え
   - パフォーマンステストの実行

## テスト項目

### 単体テスト
- [ ] キャッシュマネージャーの各メソッドのテスト
- [ ] 最適化されたオーケストレーターのテスト
- [ ] リソースマネージャーのテスト

### 統合テスト
- [ ] 最適化されたエンドポイントの動作テスト
- [ ] キャッシュ機能の動作確認
- [ ] リソース監視の動作確認

### パフォーマンステスト
- [ ] 最適化前後の処理時間比較
- [ ] キャッシュヒット率の測定
- [ ] メモリ使用量の監視
- [ ] CPU使用率の監視

## 成功基準

- [ ] 処理時間が最適化前と比較して50%以上短縮される
- [ ] キャッシュヒット率が80%以上を達成する
- [ ] リソース使用量が適切に監視・管理される
- [ ] エラーハンドリングが適切に機能する
- [ ] スケーラビリティが向上する

## 技術要件

### 必須技術
- asyncio（非同期処理）
- psutil（リソース監視）
- 既存の全サービスクラス
- キャッシュ機能

### 設計原則
- パフォーマンス最適化
- リソース効率性
- スケーラビリティ
- エラーハンドリングの統一

## 関連チケット

- **P4-001**: 統合APIエンドポイントの定義と実装
- **P4-002**: 統一された処理フローの構築
- **P4-003**: レスポンス形式の定義と実装
- **P4-004**: 個別APIエンドポイントの定義と実装
- **P4-006**: API仕様書の整備とドキュメント化

## 注意事項

- キャッシュの有効期限設定が重要
- リソース監視の閾値設定を慎重に行う
- パフォーマンステストの継続的な実行
- メモリリークの防止
