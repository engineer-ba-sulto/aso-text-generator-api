import os
import tempfile

import pandas as pd
import pytest

from app.models.csv_models import CSVData, KeywordData
from app.services.csv_validator import CSVValidator
from app.utils.exceptions import CSVValidationError


class TestCSVValidator:
    """CSV検証機能のテストクラス"""

    def setup_method(self):
        """テスト前の準備"""
        self.validator = CSVValidator()

    def test_validate_file_structure_valid(self):
        """正常なCSVファイル構造の検証テスト"""
        # 正常なデータフレームを作成
        df = pd.DataFrame(
            {
                "keyword": ["test1", "test2"],
                "ranking": [1, 2],
                "popularity": [50.0, 60.0],
                "difficulty": [30.0, 40.0],
            }
        )

        # 検証が成功することを確認
        result = self.validator.validate_file_structure(df)
        assert result is True

    def test_validate_file_structure_missing_columns(self):
        """必須カラムが不足している場合のテスト"""
        # 必須カラムが不足したデータフレームを作成
        df = pd.DataFrame(
            {
                "keyword": ["test1", "test2"],
                "ranking": [1, 2],
                # popularity, difficulty が不足
            }
        )

        # CSVValidationErrorが発生することを確認
        with pytest.raises(CSVValidationError) as exc_info:
            self.validator.validate_file_structure(df)

        assert "必須カラムが不足しています" in str(exc_info.value)

    def test_validate_file_structure_wrong_data_type(self):
        """データ型が不正な場合のテスト"""
        # データ型が不正なデータフレームを作成
        df = pd.DataFrame(
            {
                "keyword": [1, 2],  # 文字列ではなく数値
                "ranking": [1, 2],
                "popularity": [50.0, 60.0],
                "difficulty": [30.0, 40.0],
            }
        )

        # CSVValidationErrorが発生することを確認
        with pytest.raises(CSVValidationError) as exc_info:
            self.validator.validate_file_structure(df)

        assert "keyword カラムは文字列型である必要があります" in str(exc_info.value)

    def test_validate_file_structure_wrong_ranking_data_type(self):
        """rankingカラムのデータ型が不正な場合のテスト"""
        # rankingカラムが文字列型のデータフレームを作成
        df = pd.DataFrame(
            {
                "keyword": ["test1", "test2"],
                "ranking": ["1", "2"],  # 文字列型
                "popularity": [50.0, 60.0],
                "difficulty": [30.0, 40.0],
            }
        )

        # CSVValidationErrorが発生することを確認
        with pytest.raises(CSVValidationError) as exc_info:
            self.validator.validate_file_structure(df)

        assert "ranking カラムは数値型である必要があります" in str(exc_info.value)

    def test_validate_data_ranges_valid(self):
        """正常なデータ範囲の検証テスト"""
        # 正常な範囲のデータフレームを作成
        df = pd.DataFrame(
            {
                "keyword": ["test1", "test2"],
                "ranking": [1, 1000],
                "popularity": [0.0, 100.0],
                "difficulty": [0.0, 100.0],
            }
        )

        # 検証が成功することを確認
        result = self.validator.validate_data_ranges(df)
        assert result is True

    def test_validate_data_ranges_invalid_ranking(self):
        """ランキング範囲が不正な場合のテスト"""
        # 不正なランキング範囲のデータフレームを作成
        df = pd.DataFrame(
            {
                "keyword": ["test1", "test2"],
                "ranking": [0, 1001],  # 範囲外
                "popularity": [50.0, 60.0],
                "difficulty": [30.0, 40.0],
            }
        )

        # CSVValidationErrorが発生することを確認
        with pytest.raises(CSVValidationError) as exc_info:
            self.validator.validate_data_ranges(df)

        assert "ranking は 1-1000 の範囲である必要があります" in str(exc_info.value)

    def test_validate_data_ranges_invalid_popularity(self):
        """人気度範囲が不正な場合のテスト"""
        # 不正な人気度範囲のデータフレームを作成
        df = pd.DataFrame(
            {
                "keyword": ["test1", "test2"],
                "ranking": [1, 2],
                "popularity": [-1.0, 101.0],  # 範囲外
                "difficulty": [30.0, 40.0],
            }
        )

        # CSVValidationErrorが発生することを確認
        with pytest.raises(CSVValidationError) as exc_info:
            self.validator.validate_data_ranges(df)

        assert "popularity は 0-100 の範囲である必要があります" in str(exc_info.value)

    def test_validate_data_ranges_invalid_difficulty(self):
        """難易度範囲が不正な場合のテスト"""
        # 不正な難易度範囲のデータフレームを作成
        df = pd.DataFrame(
            {
                "keyword": ["test1", "test2"],
                "ranking": [1, 2],
                "popularity": [50.0, 60.0],
                "difficulty": [-1.0, 101.0],  # 範囲外
            }
        )

        # CSVValidationErrorが発生することを確認
        with pytest.raises(CSVValidationError) as exc_info:
            self.validator.validate_data_ranges(df)

        assert "difficulty は 0-100 の範囲である必要があります" in str(exc_info.value)

    def test_load_and_validate_csv_valid(self):
        """正常なCSVファイルの読み込み・検証テスト"""
        # 正常なCSVファイルを作成
        csv_content = "keyword,ranking,popularity,difficulty\ntest1,1,50.0,30.0\ntest2,2,60.0,40.0"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_file_path = f.name

        try:
            # CSVファイルを読み込み・検証
            result = self.validator.load_and_validate_csv(temp_file_path)

            # 結果を確認
            assert isinstance(result, CSVData)
            assert len(result.keywords) == 2
            assert result.keywords[0].keyword == "test1"
            assert result.keywords[0].ranking == 1
            assert result.keywords[0].popularity == 50.0
            assert result.keywords[0].difficulty == 30.0

        finally:
            # 一時ファイルを削除
            os.unlink(temp_file_path)

    def test_load_and_validate_csv_empty_file(self):
        """空のCSVファイルのテスト"""
        # 空のCSVファイルを作成
        csv_content = ""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_file_path = f.name

        try:
            # CSVValidationErrorが発生することを確認
            with pytest.raises(CSVValidationError) as exc_info:
                self.validator.load_and_validate_csv(temp_file_path)

            assert "CSV ファイルが空です" in str(exc_info.value)

        finally:
            # 一時ファイルを削除
            os.unlink(temp_file_path)

    def test_load_and_validate_csv_invalid_format(self):
        """不正な形式のCSVファイルのテスト"""
        # 不正な形式のCSVファイルを作成（カンマが不足）
        csv_content = "keyword,ranking,popularity,difficulty\ntest1,1,50.0,30.0\ntest2,2,60.0,40.0,extra_column"  # カラム数が多すぎる

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_file_path = f.name

        try:
            # CSVValidationErrorが発生することを確認
            with pytest.raises(CSVValidationError) as exc_info:
                self.validator.load_and_validate_csv(temp_file_path)

            # データ変換時にエラーが発生することを確認
            assert "CSV ファイルの形式が不正です" in str(
                exc_info.value
            ) or "difficulty は 0-100 の範囲である必要があります" in str(exc_info.value)

        finally:
            # 一時ファイルを削除
            os.unlink(temp_file_path)


class TestCSVDataModels:
    """CSVデータモデルのテストクラス"""

    def test_keyword_data_valid(self):
        """正常なキーワードデータのテスト"""
        keyword_data = KeywordData(
            keyword="test_keyword", ranking=1, popularity=50.0, difficulty=30.0
        )

        assert keyword_data.keyword == "test_keyword"
        assert keyword_data.ranking == 1
        assert keyword_data.popularity == 50.0
        assert keyword_data.difficulty == 30.0

    def test_keyword_data_empty_keyword(self):
        """空のキーワードのテスト"""
        with pytest.raises(ValueError) as exc_info:
            KeywordData(
                keyword="   ",  # 空白文字のみ
                ranking=1,
                popularity=50.0,
                difficulty=30.0,
            )

        assert "キーワードは空文字列であってはいけません" in str(exc_info.value)

    def test_keyword_data_invalid_ranking(self):
        """不正なランキングのテスト"""
        with pytest.raises(ValueError):
            KeywordData(
                keyword="test", ranking=0, popularity=50.0, difficulty=30.0  # 範囲外
            )

    def test_csv_data_valid(self):
        """正常なCSVデータのテスト"""
        keywords = [
            KeywordData(keyword="test1", ranking=1, popularity=50.0, difficulty=30.0),
            KeywordData(keyword="test2", ranking=2, popularity=60.0, difficulty=40.0),
        ]

        csv_data = CSVData(keywords=keywords)
        assert len(csv_data.keywords) == 2

    def test_csv_data_duplicate_keywords(self):
        """重複キーワードのテスト"""
        keywords = [
            KeywordData(keyword="test", ranking=1, popularity=50.0, difficulty=30.0),
            KeywordData(
                keyword="TEST", ranking=2, popularity=60.0, difficulty=40.0
            ),  # 大文字小文字の違い
        ]

        with pytest.raises(ValueError) as exc_info:
            CSVData(keywords=keywords)

        assert "重複するキーワードが存在します" in str(exc_info.value)

    def test_csv_data_empty_keywords(self):
        """空のキーワードリストのテスト"""
        with pytest.raises(ValueError):
            CSVData(keywords=[])
