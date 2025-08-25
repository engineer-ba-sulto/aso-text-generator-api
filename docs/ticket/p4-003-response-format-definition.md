# P4-003: レスポンス形式の定義と実装

## 概要

統合APIエンドポイントと個別APIエンドポイントで使用する統一されたレスポンス形式を定義し、生成された全項目を構造化されたJSON形式で返す機能を実装します。レスポンスのキーは共通ですが、値（生成されたテキスト）は指定された言語になります。

## 目標

- 統一されたレスポンス形式の設計
- 多言語対応のレスポンス実装
- エラー時のレスポンス形式の統一
- API仕様書との整合性確保

## 実装内容

### 1. 統合レスポンスモデルの定義

```python
# app/models/response_models.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class ASOTextGenerationResponse(BaseModel):
    """
    ASOテキスト生成の統合レスポンスモデル
    """
    # 生成されたテキスト項目
    keyword_field: str = Field(
        ..., 
        description="キーワードフィールド (100文字以内)",
        max_length=100
    )
    title: str = Field(
        ..., 
        description="アプリタイトル (30文字以内)",
        max_length=30
    )
    subtitle: str = Field(
        ..., 
        description="サブタイトル (30文字以内)",
        max_length=30
    )
    description: str = Field(
        ..., 
        description="アプリ概要 (4000文字以内)",
        max_length=4000
    )
    whats_new: str = Field(
        ..., 
        description="最新情報 (4000文字以内)",
        max_length=4000
    )
    
    # メタデータ
    language: str = Field(
        ..., 
        description="生成された言語 (ja: 日本語, en: 英語)"
    )
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="生成日時 (UTC)"
    )
    
    # 処理情報
    processing_time: Optional[float] = Field(
        None,
        description="処理時間（秒）"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "keyword_field": "フィットネス トレーニング 健康管理 運動記録",
                "title": "FitTracker - 健康管理アプリ",
                "subtitle": "あなたの健康をサポート",
                "description": "FitTrackerは、あなたの健康管理をサポートする総合的なフィットネスアプリです。...",
                "whats_new": "新機能として、より詳細な運動分析機能を追加しました。...",
                "language": "ja",
                "generated_at": "2024-01-15T10:30:00Z",
                "processing_time": 2.5
            }
        }
```

### 2. 個別レスポンスモデルの定義

```python
# app/models/response_models.py
class KeywordFieldResponse(BaseModel):
    """キーワードフィールド生成のレスポンスモデル"""
    keyword_field: str = Field(..., description="キーワードフィールド (100文字以内)", max_length=100)
    language: str = Field(..., description="生成された言語")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = Field(None, description="処理時間（秒）")

class TitleResponse(BaseModel):
    """タイトル生成のレスポンスモデル"""
    title: str = Field(..., description="アプリタイトル (30文字以内)", max_length=30)
    language: str = Field(..., description="生成された言語")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = Field(None, description="処理時間（秒）")

class SubtitleResponse(BaseModel):
    """サブタイトル生成のレスポンスモデル"""
    subtitle: str = Field(..., description="サブタイトル (30文字以内)", max_length=30)
    language: str = Field(..., description="生成された言語")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = Field(None, description="処理時間（秒）")

class DescriptionResponse(BaseModel):
    """概要生成のレスポンスモデル"""
    description: str = Field(..., description="アプリ概要 (4000文字以内)", max_length=4000)
    language: str = Field(..., description="生成された言語")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = Field(None, description="処理時間（秒）")

class WhatsNewResponse(BaseModel):
    """最新情報生成のレスポンスモデル"""
    whats_new: str = Field(..., description="最新情報 (4000文字以内)", max_length=4000)
    language: str = Field(..., description="生成された言語")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = Field(None, description="処理時間（秒）")
```

### 3. エラーレスポンスモデルの定義

```python
# app/models/error_models.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class ErrorResponse(BaseModel):
    """
    エラーレスポンスの統一モデル
    """
    error: str = Field(..., description="エラーメッセージ")
    error_code: str = Field(..., description="エラーコード")
    detail: Optional[str] = Field(None, description="詳細なエラー情報")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = Field(None, description="エラーが発生したエンドポイント")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Invalid language parameter",
                "error_code": "INVALID_LANGUAGE",
                "detail": "Language must be either 'ja' or 'en'",
                "timestamp": "2024-01-15T10:30:00Z",
                "path": "/api/v1/generate-aso-texts"
            }
        }

class ValidationErrorResponse(BaseModel):
    """
    バリデーションエラーのレスポンスモデル
    """
    error: str = Field(default="Validation Error", description="エラーメッセージ")
    error_code: str = Field(default="VALIDATION_ERROR", description="エラーコード")
    validation_errors: Dict[str, Any] = Field(..., description="バリデーションエラーの詳細")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

### 4. レスポンスビルダーの実装

```python
# app/utils/response_builder.py
from typing import Dict, Any, Optional
from datetime import datetime
import time
from app.models.response_models import (
    ASOTextGenerationResponse,
    KeywordFieldResponse,
    TitleResponse,
    SubtitleResponse,
    DescriptionResponse,
    WhatsNewResponse
)

class ResponseBuilder:
    """レスポンス構築のユーティリティクラス"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def build_integrated_response(
        self,
        keyword_field: str,
        title: str,
        subtitle: str,
        description: str,
        whats_new: str,
        language: str
    ) -> ASOTextGenerationResponse:
        """
        統合レスポンスを構築
        
        Args:
            keyword_field: キーワードフィールド
            title: タイトル
            subtitle: サブタイトル
            description: 概要
            whats_new: 最新情報
            language: 生成言語
            
        Returns:
            ASOTextGenerationResponse: 統合レスポンス
        """
        processing_time = time.time() - self.start_time
        
        return ASOTextGenerationResponse(
            keyword_field=keyword_field,
            title=title,
            subtitle=subtitle,
            description=description,
            whats_new=whats_new,
            language=language,
            processing_time=round(processing_time, 2)
        )
    
    def build_keyword_field_response(
        self,
        keyword_field: str,
        language: str
    ) -> KeywordFieldResponse:
        """キーワードフィールドレスポンスを構築"""
        processing_time = time.time() - self.start_time
        
        return KeywordFieldResponse(
            keyword_field=keyword_field,
            language=language,
            processing_time=round(processing_time, 2)
        )
    
    def build_title_response(
        self,
        title: str,
        language: str
    ) -> TitleResponse:
        """タイトルレスポンスを構築"""
        processing_time = time.time() - self.start_time
        
        return TitleResponse(
            title=title,
            language=language,
            processing_time=round(processing_time, 2)
        )
    
    def build_subtitle_response(
        self,
        subtitle: str,
        language: str
    ) -> SubtitleResponse:
        """サブタイトルレスポンスを構築"""
        processing_time = time.time() - self.start_time
        
        return SubtitleResponse(
            subtitle=subtitle,
            language=language,
            processing_time=round(processing_time, 2)
        )
    
    def build_description_response(
        self,
        description: str,
        language: str
    ) -> DescriptionResponse:
        """概要レスポンスを構築"""
        processing_time = time.time() - self.start_time
        
        return DescriptionResponse(
            description=description,
            language=language,
            processing_time=round(processing_time, 2)
        )
    
    def build_whats_new_response(
        self,
        whats_new: str,
        language: str
    ) -> WhatsNewResponse:
        """最新情報レスポンスを構築"""
        processing_time = time.time() - self.start_time
        
        return WhatsNewResponse(
            whats_new=whats_new,
            language=language,
            processing_time=round(processing_time, 2)
        )
```

### 5. エンドポイントでのレスポンスビルダー使用

```python
# app/api/v1/aso_endpoints.py
from app.utils.response_builder import ResponseBuilder
from fastapi import Depends

@router.post("/generate-aso-texts", response_model=ASOTextGenerationResponse)
async def generate_aso_texts(
    request: ASOTextGenerationRequest,
    orchestrator: ASOTextOrchestrator = Depends(),
    response_builder: ResponseBuilder = Depends()
):
    """ASOテキストを一括生成するエンドポイント"""
    try:
        # テキスト生成の実行
        result = await orchestrator.generate_all_texts(
            csv_file=request.csv_file,
            app_name=request.app_name,
            features=request.features,
            language=request.language
        )
        
        # レスポンスの構築
        return response_builder.build_integrated_response(
            keyword_field=result.keyword_field,
            title=result.title,
            subtitle=result.subtitle,
            description=result.description,
            whats_new=result.whats_new,
            language=result.language
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"テキスト生成中にエラーが発生しました: {str(e)}"
        )

@router.post("/generate-keyword-field", response_model=KeywordFieldResponse)
async def generate_keyword_field(
    request: KeywordFieldRequest,
    keyword_field_generator: KeywordFieldGenerator = Depends(),
    response_builder: ResponseBuilder = Depends()
):
    """キーワードフィールド生成エンドポイント"""
    try:
        keyword_field = await keyword_field_generator.generate(
            request.keywords_data,
            request.primary_keyword,
            request.language
        )
        
        return response_builder.build_keyword_field_response(
            keyword_field=keyword_field,
            language=request.language
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"キーワードフィールド生成中にエラーが発生しました: {str(e)}"
        )
```

## 実装手順

1. **レスポンスモデルの作成**
   - `app/models/response_models.py`に統合レスポンスモデルを追加
   - 個別レスポンスモデルを追加
   - エラーレスポンスモデルを追加

2. **レスポンスビルダーの実装**
   - `app/utils/response_builder.py`を作成
   - 各レスポンスタイプのビルダーメソッドを実装

3. **エンドポイントの更新**
   - レスポンスビルダーを使用するように更新
   - 適切なレスポンスモデルを指定

4. **エラーハンドリングの統一**
   - エラーレスポンス形式の統一
   - 適切なHTTPステータスコードの設定

## テスト項目

### 単体テスト
- [ ] 各レスポンスモデルのバリデーションテスト
- [ ] レスポンスビルダーの各メソッドのテスト
- [ ] 文字数制限のテスト

### 統合テスト
- [ ] 統合エンドポイントのレスポンス形式テスト
- [ ] 個別エンドポイントのレスポンス形式テスト
- [ ] エラーレスポンスの形式テスト

### パフォーマンステスト
- [ ] レスポンス構築時間の測定
- [ ] メモリ使用量の確認

## 成功基準

- [ ] 統一されたレスポンス形式が正しく実装されている
- [ ] 多言語対応のレスポンスが正常に動作する
- [ ] エラーレスポンスが適切に形式化されている
- [ ] 文字数制限が正しく適用されている
- [ ] 処理時間が正確に記録されている

## 技術要件

### 必須技術
- Pydantic（レスポンスモデル）
- FastAPI（レスポンス形式）
- 既存のサービスクラス

### 設計原則
- レスポンス形式の一貫性
- エラーハンドリングの統一
- パフォーマンスの考慮
- API仕様書との整合性

## 関連チケット

- **P4-001**: 統合APIエンドポイントの定義と実装
- **P4-002**: 統一された処理フローの構築
- **P4-004**: 個別APIエンドポイントの定義と実装
- **P0-005**: エラーハンドリング（基盤）

## 注意事項

- レスポンス形式の一貫性を保つ
- 文字数制限の厳格な適用
- エラーレスポンスの統一性確保
- 処理時間の正確な記録
