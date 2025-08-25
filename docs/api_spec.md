# ASO Text Generator API 仕様書

## 概要

ASO Text Generator API は、App Store Optimization（ASO）のためのテキスト生成を行う API です。

## エンドポイント

### 1. CSV 分析エンドポイント

#### POST /api/v1/analyze-csv

CSV ファイルを分析し、キーワードを抽出します。

**リクエスト:**

- Content-Type: multipart/form-data
- Body: CSV ファイル

**レスポンス:**

```json
{
  "success": true,
  "analysis_result": {
    "total_rows": 100,
    "keywords_found": 50
  },
  "extracted_keywords": ["keyword1", "keyword2", ...],
  "summary": "分析サマリー"
}
```

### 2. テキスト生成エンドポイント

#### POST /api/v1/generate-text

ASO テキストを生成します。

**リクエスト:**

```json
{
  "app_name": "アプリ名",
  "app_description": "アプリの説明",
  "keywords": ["keyword1", "keyword2"],
  "target_language": "ja",
  "text_type": "title",
  "additional_info": {}
}
```

**レスポンス:**

```json
{
  "success": true,
  "generated_text": "生成されたテキスト",
  "text_type": "title",
  "language": "ja",
  "metadata": {}
}
```

### 3. キーワード選定エンドポイント

#### POST /api/v1/select-keywords

キーワードを選定します。

**リクエスト:**

```json
{
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "target_count": 10,
  "selection_criteria": {}
}
```

**レスポンス:**

```json
{
  "success": true,
  "selected_keywords": ["selected1", "selected2"],
  "priority_scores": {
    "selected1": 0.9,
    "selected2": 0.8
  },
  "reasoning": "選定理由"
}
```

## エラーレスポンス

```json
{
  "success": false,
  "error_code": "ERROR_CODE",
  "error_message": "エラーメッセージ",
  "details": {}
}
```

## 認証

現在は認証不要です。

## レート制限

現在は制限なしです。
