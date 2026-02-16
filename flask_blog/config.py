"""
Flask 博客系统配置文件
包含数据库配置、安全配置等
"""

import os
from datetime import timedelta

# 获取项目根目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """
    基础配置类
    包含所有环境的通用配置
    """

    # ==================== Flask 基础配置 ====================
    # 密钥（用于 session、CSRF 保护等，生产环境请使用随机生成的复杂字符串）
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'

    # ==================== 数据库配置 ====================
    # SQLite 数据库文件路径
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'blog.db')

    # 关闭 SQLAlchemy 的事件通知系统，节省内存
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ==================== 分页配置 ====================
    # 每页显示的文章数量
    POSTS_PER_PAGE = 5

    # 后台管理每页显示数量
    ADMIN_PER_PAGE = 10

    # ==================== Session 配置 ====================
    # Session 过期时间（1小时）
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    # ==================== 管理员账号配置 ====================
    # 默认管理员账号（首次初始化时使用）
    DEFAULT_ADMIN_USERNAME = 'admin'
    DEFAULT_ADMIN_PASSWORD = 'admin123'  # 生产环境请务必修改


class DevelopmentConfig(Config):
    """
    开发环境配置
    开启调试模式
    """
    DEBUG = True


class ProductionConfig(Config):
    """
    生产环境配置
    关闭调试模式，启用安全设置
    """
    DEBUG = False


class TestingConfig(Config):
    """
    测试环境配置
    使用内存数据库，方便测试
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# 配置字典，方便根据环境变量切换
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}