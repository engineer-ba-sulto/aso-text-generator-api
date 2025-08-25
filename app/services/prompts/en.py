"""
英語プロンプト定義
"""


class EnglishPrompts:
    """英語プロンプトクラス"""

    # タイトル生成プロンプト
    TITLE_GENERATION = """
    Generate an App Store app title based on the following information.
    
    App Info: {app_info}
    Keywords: {keywords}
    
    Requirements:
    - Within 30 characters
    - Include main keywords
    - Attractive and memorable
    - Appropriately express app functionality
    
    Generated title:
    """

    # 説明文生成プロンプト
    DESCRIPTION_GENERATION = """
    Generate an App Store app description based on the following information.
    
    App Info: {app_info}
    Keywords: {keywords}
    
    Requirements:
    - Within 4000 characters
    - Naturally incorporate main keywords
    - Clearly state app value proposition
    - Emphasize user problem solving
    
    Generated description:
    """

    # キーワード文字列生成プロンプト
    KEYWORDS_GENERATION = """
    Generate an App Store keyword string based on the following keywords.
    
    Keywords: {keywords}
    
    Requirements:
    - Within 100 characters
    - Comma separated
    - Ordered by relevance
    - Consider competitive analysis
    
    Generated keyword string:
    """
