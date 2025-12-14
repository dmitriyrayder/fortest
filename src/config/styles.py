"""CSS стили для приложения"""

CSS_STYLES = """
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(120deg, #1f77b4, #667eea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }

    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.3);
    }

    .insight-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        border-left: 5px solid #fff;
    }

    .problem-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 5px solid #ee5a6f;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        color: white;
        font-weight: 500;
    }

    .accuracy-card {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        color: white;
    }
</style>
"""
