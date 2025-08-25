import pandas as pd
from typing import List
from app.models.csv_models import CSVData, KeywordData
from app.utils.exceptions import CSVValidationError


class CSVValidator:
    """CSV ファイル検証クラス"""

    REQUIRED_COLUMNS = ['keyword', 'ranking', 'popularity', 'difficulty']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def validate_file_structure(self, df: pd.DataFrame) -> bool:
        """CSV ファイルの構造を検証"""
        # 必須カラムの存在チェック
        missing_columns = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_columns:
            raise CSVValidationError(f"必須カラムが不足しています: {missing_columns}")

        # データ型チェック
        if not pd.api.types.is_string_dtype(df['keyword']):
            raise CSVValidationError("keyword カラムは文字列型である必要があります")

        if not pd.api.types.is_numeric_dtype(df['ranking']):
            raise CSVValidationError("ranking カラムは数値型である必要があります")

        return True

    def validate_data_ranges(self, df: pd.DataFrame) -> bool:
        """データの値範囲を検証"""
        # ランキング範囲チェック（1-1000）
        if not (df['ranking'] >= 1).all() or not (df['ranking'] <= 1000).all():
            raise CSVValidationError("ranking は 1-1000 の範囲である必要があります")

        # 人気度範囲チェック（0-100）
        if not (df['popularity'] >= 0).all() or not (df['popularity'] <= 100).all():
            raise CSVValidationError("popularity は 0-100 の範囲である必要があります")

        # 難易度範囲チェック（0-100）
        if not (df['difficulty'] >= 0).all() or not (df['difficulty'] <= 100).all():
            raise CSVValidationError("difficulty は 0-100 の範囲である必要があります")

        return True

    def load_and_validate_csv(self, file_path: str) -> CSVData:
        """CSV ファイルを読み込み、検証してデータモデルに変換"""
        try:
            df = pd.read_csv(file_path)

            # 構造検証
            self.validate_file_structure(df)

            # 値範囲検証
            self.validate_data_ranges(df)

            # データモデルに変換
            keywords = []
            for _, row in df.iterrows():
                keyword_data = KeywordData(
                    keyword=row['keyword'],
                    ranking=int(row['ranking']),
                    popularity=float(row['popularity']),
                    difficulty=float(row['difficulty'])
                )
                keywords.append(keyword_data)

            return CSVData(keywords=keywords)

        except pd.errors.EmptyDataError:
            raise CSVValidationError("CSV ファイルが空です")
        except pd.errors.ParserError:
            raise CSVValidationError("CSV ファイルの形式が不正です")
