from typing import List, Optional

import pandas as pd
from pydantic import BaseModel, Field, field_validator


class KeywordData(BaseModel):
    """個別キーワードデータモデル"""

    keyword: str = Field(..., min_length=1, max_length=100, description="キーワード")
    ranking: int = Field(..., ge=1, le=1000, description="ランキング（1-1000）")
    popularity: float = Field(..., ge=0.0, le=100.0, description="人気度（0-100）")
    difficulty: float = Field(..., ge=0.0, le=100.0, description="難易度（0-100）")

    @field_validator("keyword")
    @classmethod
    def validate_keyword(cls, v):
        if not v.strip():
            raise ValueError("キーワードは空文字列であってはいけません")
        return v.strip()


class CSVData(BaseModel):
    """CSV ファイル全体のデータモデル"""

    keywords: List[KeywordData] = Field(..., min_length=1, max_length=1000)

    @field_validator("keywords")
    @classmethod
    def validate_unique_keywords(cls, v):
        keywords = [k.keyword.lower() for k in v]
        if len(keywords) != len(set(keywords)):
            raise ValueError("重複するキーワードが存在します")
        return v


class PydanticScoringResult(BaseModel):
    """スコアリング結果モデル"""

    keyword_data: KeywordData
    composite_score: float = Field(..., ge=0.0, le=1.0, description="複合スコア（0-1）")
    ranking_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="ランキングスコア（0-1）"
    )
    popularity_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="人気度スコア（0-1）"
    )
    difficulty_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="難易度スコア（0-1）"
    )


class ScoringResults(BaseModel):
    """スコアリング結果リストモデル"""

    results: List[PydanticScoringResult] = Field(
        ..., min_length=1, description="スコアリング結果のリスト"
    )
    total_count: int = Field(..., ge=1, description="総キーワード数")
    average_score: float = Field(..., ge=0.0, le=1.0, description="平均スコア")
