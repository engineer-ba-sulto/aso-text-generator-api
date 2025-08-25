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

    # サブタイトル生成プロンプト
    SUBTITLE_GENERATION = """
    Generate an App Store app subtitle based on the following information.
    
    App Name: {app_name}
    App Features: {app_features}
    Target Audience: {target_audience}
    
    Requirements:
    - Within 30 characters (strictly enforced)
    - Exclude main keyword ({main_keyword})
    - Express app value attractively
    - Memorable and impressive expression
    - Concisely convey app functionality and features
    
    Generated subtitle:
    """

    # 概要生成プロンプト
    DESCRIPTION_GENERATION = """
    Generate an App Store app description based on the following information.
    
    App Name: {app_name}
    App Features: {app_features}
    Main Keyword: {main_keyword}
    Related Keywords: {related_keywords}
    Target Audience: {target_audience}
    
    Requirements:
    - Within 4000 characters (strictly enforced)
    - Naturally include main keyword ({main_keyword}) 4-7 times
    - Clearly explain app value proposition
    - Emphasize user problem solving
    - Detail app's main features
    - Show specific benefits to target users
    - Readable and attractive text structure
    
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
