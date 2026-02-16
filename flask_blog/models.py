"""
Flask 博客系统数据模型
定义数据库表结构和关系
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# 初始化 SQLAlchemy 实例
# 注意：不在此处传入 app，在 app.py 中初始化
db = SQLAlchemy()


# ==================== 关联表（多对多关系）====================
# 文章与标签的多对多关联表
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class Post(db.Model):
    """
    文章模型
    存储博客文章的所有信息
    """
    __tablename__ = 'posts'  # 数据库表名

    # 主键，自增ID
    id = db.Column(db.Integer, primary_key=True)

    # 文章标题，最大长度200，不允许为空，建立索引加速查询
    title = db.Column(db.String(200), nullable=False, index=True)

    # 文章摘要/简介，最大长度500，可为空
    # 如果不填写摘要，系统会自动从正文截取前200字符
    summary = db.Column(db.String(500), nullable=True)

    # 文章内容，使用 Text 类型存储长文本，不允许为空
    content = db.Column(db.Text, nullable=False)

    # 创建时间，默认值为当前时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 更新时间，每次修改时自动更新
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 浏览次数，默认0
    views = db.Column(db.Integer, default=0)

    # 是否发布（草稿/已发布），默认True表示已发布
    is_published = db.Column(db.Boolean, default=True)

    # 外键：分类ID，关联到 categories 表
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    # 关系：与分类的多对一关系
    # backref='posts' 表示在 Category 模型中可以通过 category.posts 访问该分类下的所有文章
    category = db.relationship('Category', backref=db.backref('posts', lazy='dynamic'))

    # 关系：与标签的多对多关系
    # secondary=post_tags 指定关联表
    # lazy='dynamic' 表示延迟加载，需要用的时候才查询
    tags = db.relationship('Tag', secondary=post_tags, lazy='dynamic',
                          backref=db.backref('posts', lazy='dynamic'))

    # 关系：与评论的一对多关系
    # cascade='all, delete-orphan' 表示删除文章时同时删除相关评论
    comments = db.relationship('Comment', backref='post', lazy='dynamic',
                               cascade='all, delete-orphan')

    def __init__(self, title, content, category_id, summary=None, is_published=True):
        """
        文章初始化方法

        Args:
            title: 文章标题
            content: 文章内容
            category_id: 分类ID
            summary: 文章摘要（可选）
            is_published: 是否发布（可选，默认True）
        """
        self.title = title
        self.content = content
        self.category_id = category_id
        self.is_published = is_published
        # 如果没有提供摘要，自动从正文生成
        self.summary = summary or self.generate_summary()

    def generate_summary(self, length=200):
        """
        自动生成文章摘要
        从正文截取前指定长度的字符

        Args:
            length: 摘要长度，默认200字符

        Returns:
            生成的摘要字符串
        """
        # 去除 HTML 标签（如果有的话）
        import re
        text = re.sub(r'<[^>]+>', '', self.content)
        # 截取前 length 个字符，如果内容更长则添加省略号
        if len(text) > length:
            return text[:length] + '...'
        return text

    def increment_views(self):
        """
        增加浏览次数
        用于文章详情页被访问时调用
        """
        self.views += 1
        db.session.commit()

    def __repr__(self):
        """对象的字符串表示，方便调试"""
        return f'<Post {self.title}>'

    @property
    def comment_count(self):
        """
        获取文章评论数量
        使用 property 装饰器，可以像访问属性一样访问方法
        """
        return self.comments.count()


class Category(db.Model):
    """
    分类模型
    用于对文章进行分类管理
    """
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)

    # 分类名称，唯一，不允许为空
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)

    # 分类描述，可选
    description = db.Column(db.String(200), nullable=True)

    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return f'<Category {self.name}>'

    @property
    def post_count(self):
        """获取该分类下的文章数量"""
        return self.posts.filter_by(is_published=True).count()


class Tag(db.Model):
    """
    标签模型
    用于给文章打标签，方便检索
    """
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)

    # 标签名称，唯一，不允许为空
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)

    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Tag {self.name}>'

    @property
    def post_count(self):
        """获取使用该标签的文章数量"""
        return self.posts.filter_by(is_published=True).count()


class Comment(db.Model):
    """
    评论模型
    存储文章的评论信息
    """
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)

    # 评论者昵称，最大长度50，不允许为空
    author = db.Column(db.String(50), nullable=False)

    # 评论者邮箱，最大长度100，不允许为空
    email = db.Column(db.String(100), nullable=False)

    # 评论内容，不允许为空
    content = db.Column(db.Text, nullable=False)

    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 外键：关联的文章ID
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

    def __init__(self, author, email, content, post_id):
        self.author = author
        self.email = email
        self.content = content
        self.post_id = post_id

    def __repr__(self):
        return f'<Comment by {self.author} on Post {self.post_id}>'


class Admin(db.Model):
    """
    管理员模型
    存储管理员账号信息
    """
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)

    # 管理员用户名，唯一，不允许为空
    username = db.Column(db.String(50), unique=True, nullable=False)

    # 密码哈希值，不允许为空
    # 实际存储的是加密后的密码，不是明文
    password_hash = db.Column(db.String(255), nullable=False)

    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 最后登录时间
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        """
        设置密码
        使用 Werkzeug 的密码哈希功能加密存储

        Args:
            password: 明文密码
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        验证密码

        Args:
            password: 明文密码

        Returns:
            密码是否正确（布尔值）
        """
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def __repr__(self):
        return f'<Admin {self.username}>'


# ==================== 数据库操作辅助函数 ====================

def init_db(app):
    """
    初始化数据库
    创建所有表结构

    Args:
        app: Flask 应用实例
    """
    with app.app_context():
        db.create_all()


def create_default_data(app):
    """
    创建默认数据
    包括默认管理员账号、示例分类等

    Args:
        app: Flask 应用实例
    """
    with app.app_context():
        from config import Config

        # 创建默认管理员账号（如果不存在）
        if not Admin.query.filter_by(username=Config.DEFAULT_ADMIN_USERNAME).first():
            admin = Admin(
                username=Config.DEFAULT_ADMIN_USERNAME,
                password=Config.DEFAULT_ADMIN_PASSWORD
            )
            db.session.add(admin)
            print(f"创建默认管理员账号: {Config.DEFAULT_ADMIN_USERNAME}")

        # 创建默认分类（如果不存在）
        default_categories = ['技术', '生活', '随笔', '教程']
        for cat_name in default_categories:
            if not Category.query.filter_by(name=cat_name).first():
                category = Category(name=cat_name)
                db.session.add(category)
                print(f"创建默认分类: {cat_name}")

        db.session.commit()
        print("默认数据创建完成！")