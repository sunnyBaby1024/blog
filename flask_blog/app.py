"""
Flask 个人博客系统 - 主程序入口
包含所有路由定义、视图函数和业务逻辑

运行方式:
    开发环境: python app.py
    生产环境: 建议使用 Gunicorn: gunicorn -w 4 -b 0.0.0.0:5000 app:app
"""

from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, abort, jsonify
)

# 导入配置
from config import config

# 导入数据模型
from models import db, Post, Category, Tag, Comment, Admin

# ==================== Flask 应用初始化 ====================

def create_app(config_name='default'):
    """
    应用工厂函数
    创建并配置 Flask 应用实例

    Args:
        config_name: 配置环境名称 ('development', 'production', 'testing')

    Returns:
        配置好的 Flask 应用实例
    """
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config[config_name])

    # 初始化数据库
    db.init_app(app)

    # 注册模板上下文处理器（全局变量）
    register_context_processors(app)

    # 注册错误处理
    register_error_handlers(app)

    return app


# ==================== 登录验证装饰器 ====================

def login_required(f):
    """
    登录验证装饰器
    用于保护需要管理员权限的路由

    使用方法:
        @app.route('/admin/dashboard')
        @login_required
        def dashboard():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查 session 中是否有 admin_id
        if 'admin_id' not in session:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== 上下文处理器 ====================

def register_context_processors(app):
    """
    注册模板全局变量
    这些变量在所有模板中都可以直接使用
    """

    @app.context_processor
    def inject_common_data():
        """
        注入通用数据到模板上下文
        包括分类列表、标签云、最新文章等
        """
        # 获取所有分类及其文章数量
        categories = Category.query.all()

        # 获取所有标签（用于标签云）
        tags = Tag.query.all()

        # 获取最新文章（侧边栏显示）
        recent_posts = Post.query.filter_by(is_published=True) \
                                 .order_by(Post.created_at.desc()) \
                                 .limit(5).all()

        # 获取热门文章（按浏览量排序）
        popular_posts = Post.query.filter_by(is_published=True) \
                                  .order_by(Post.views.desc()) \
                                  .limit(5).all()

        return dict(
            categories=categories,
            tags=tags,
            recent_posts=recent_posts,
            popular_posts=popular_posts,
            now=datetime.utcnow()
        )


# ==================== 错误处理 ====================

def register_error_handlers(app):
    """注册错误处理函数"""

    @app.errorhandler(404)
    def not_found_error(error):
        """404 页面未找到"""
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """500 服务器内部错误"""
        db.session.rollback()  # 回滚数据库事务
        return render_template('errors/500.html'), 500


# 创建应用实例（放在函数定义之后）
app = create_app('development')


# ==================== 前台路由 ====================

@app.route('/')
def index():
    """
    首页 - 文章列表
    支持分页显示
    """
    # 获取当前页码（从 URL 参数中获取，默认为1）
    page = request.args.get('page', 1, type=int)

    # 查询已发布的文章，按发布时间倒序排列，分页显示
    pagination = Post.query.filter_by(is_published=True) \
                           .order_by(Post.created_at.desc()) \
                           .paginate(
                               page=page,
                               per_page=app.config['POSTS_PER_PAGE'],
                               error_out=False
                           )

    # 获取当前页的文章列表
    posts = pagination.items

    return render_template('index.html', posts=posts, pagination=pagination)


@app.route('/post/<int:post_id>')
def post_detail(post_id):
    """
    文章详情页

    Args:
        post_id: 文章ID
    """
    # 根据ID查询文章，如果不存在返回404
    post = Post.query.get_or_404(post_id)

    # 检查文章是否已发布（未发布的文章只有管理员能看到）
    if not post.is_published and 'admin_id' not in session:
        abort(404)

    # 增加浏览次数
    post.increment_views()

    # 获取上一篇和下一篇文章（用于导航）
    prev_post = Post.query.filter(
        Post.id < post_id,
        Post.is_published == True
    ).order_by(Post.id.desc()).first()

    next_post = Post.query.filter(
        Post.id > post_id,
        Post.is_published == True
    ).order_by(Post.id.asc()).first()

    return render_template('post.html',
                         post=post,
                         prev_post=prev_post,
                         next_post=next_post)


@app.route('/category/<int:category_id>')
def category_posts(category_id):
    """
    分类文章列表
    显示指定分类下的所有文章
    """
    # 获取分类信息
    category = Category.query.get_or_404(category_id)

    # 获取页码
    page = request.args.get('page', 1, type=int)

    # 查询该分类下的已发布文章
    pagination = Post.query.filter_by(
        category_id=category_id,
        is_published=True
    ).order_by(Post.created_at.desc()).paginate(
        page=page,
        per_page=app.config['POSTS_PER_PAGE'],
        error_out=False
    )

    return render_template('category.html',
                         category=category,
                         posts=pagination.items,
                         pagination=pagination)


@app.route('/tag/<int:tag_id>')
def tag_posts(tag_id):
    """
    标签文章列表
    显示包含指定标签的所有文章
    """
    # 获取标签信息
    tag = Tag.query.get_or_404(tag_id)

    # 获取页码
    page = request.args.get('page', 1, type=int)

    # 查询包含该标签的已发布文章
    pagination = tag.posts.filter_by(is_published=True) \
                          .order_by(Post.created_at.desc()) \
                          .paginate(
                              page=page,
                              per_page=app.config['POSTS_PER_PAGE'],
                              error_out=False
                          )

    return render_template('tag.html',
                         tag=tag,
                         posts=pagination.items,
                         pagination=pagination)


@app.route('/search')
def search():
    """
    文章搜索功能
    支持按标题和内容关键词搜索
    """
    # 获取搜索关键词
    keyword = request.args.get('q', '').strip()

    if not keyword:
        flash('请输入搜索关键词', 'warning')
        return redirect(url_for('index'))

    # 获取页码
    page = request.args.get('page', 1, type=int)

    # 搜索标题或内容包含关键词的已发布文章
    pagination = Post.query.filter(
        Post.is_published == True,
        db.or_(
            Post.title.contains(keyword),
            Post.content.contains(keyword)
        )
    ).order_by(Post.created_at.desc()).paginate(
        page=page,
        per_page=app.config['POSTS_PER_PAGE'],
        error_out=False
    )

    return render_template('search.html',
                         keyword=keyword,
                         posts=pagination.items,
                         pagination=pagination,
                         total=pagination.total)


@app.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    """
    添加评论
    接收表单提交的评论信息并保存到数据库
    """
    # 获取表单数据
    author = request.form.get('author', '').strip()
    email = request.form.get('email', '').strip()
    content = request.form.get('content', '').strip()

    # 表单验证
    if not all([author, email, content]):
        flash('请填写完整的评论信息', 'danger')
        return redirect(url_for('post_detail', post_id=post_id))

    # 验证邮箱格式（简单验证）
    if '@' not in email or '.' not in email.split('@')[-1]:
        flash('请输入有效的邮箱地址', 'danger')
        return redirect(url_for('post_detail', post_id=post_id))

    # 创建评论
    comment = Comment(
        author=author,
        email=email,
        content=content,
        post_id=post_id
    )

    try:
        db.session.add(comment)
        db.session.commit()
        flash('评论发表成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash('评论发表失败，请稍后重试', 'danger')
        app.logger.error(f'Add comment error: {e}')

    return redirect(url_for('post_detail', post_id=post_id))


# ==================== 后台管理路由 ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    """
    管理员登录页面
    """
    # 如果已登录，直接跳转到后台首页
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # 查询管理员账号
        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            # 登录成功，设置 session
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            session.permanent = True  # 使用配置的 session 过期时间

            # 更新最后登录时间
            admin.update_last_login()

            flash('登录成功！', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('用户名或密码错误', 'danger')

    return render_template('admin/login.html')


@app.route('/admin/logout')
def logout():
    """
    管理员退出登录
    """
    # 清除 session
    session.clear()
    flash('已成功退出登录', 'info')
    return redirect(url_for('index'))


@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """
    后台管理首页
    显示统计数据
    """
    # 统计各类型数据数量
    stats = {
        'total_posts': Post.query.count(),
        'published_posts': Post.query.filter_by(is_published=True).count(),
        'draft_posts': Post.query.filter_by(is_published=False).count(),
        'total_categories': Category.query.count(),
        'total_tags': Tag.query.count(),
        'total_comments': Comment.query.count()
    }

    # 获取最近发布的5篇文章
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()

    # 获取最近发表的5条评论
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_posts=recent_posts,
                         recent_comments=recent_comments)


# ==================== 文章管理路由 ====================

@app.route('/admin/posts')
@login_required
def admin_posts():
    """
    文章列表管理
    """
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')  # all, published, draft

    # 构建查询
    query = Post.query
    if status == 'published':
        query = query.filter_by(is_published=True)
    elif status == 'draft':
        query = query.filter_by(is_published=False)

    pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page,
        per_page=app.config['ADMIN_PER_PAGE'],
        error_out=False
    )

    return render_template('admin/posts.html',
                         posts=pagination.items,
                         pagination=pagination,
                         status=status)


@app.route('/admin/post/add', methods=['GET', 'POST'])
@login_required
def admin_post_add():
    """
    添加新文章
    """
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        summary = request.form.get('summary', '').strip()
        category_id = request.form.get('category_id', type=int)
        tag_ids = request.form.getlist('tags', type=int)
        is_published = request.form.get('is_published') == 'on'

        # 验证必填字段
        if not all([title, content, category_id]):
            flash('标题、内容和分类为必填项', 'danger')
        else:
            # 创建文章
            post = Post(
                title=title,
                content=content,
                summary=summary or None,
                category_id=category_id,
                is_published=is_published
            )

            # 添加标签关联
            if tag_ids:
                tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
                post.tags.extend(tags)

            try:
                db.session.add(post)
                db.session.commit()
                flash('文章发布成功！' if is_published else '草稿保存成功！', 'success')
                return redirect(url_for('admin_posts'))
            except Exception as e:
                db.session.rollback()
                flash('保存失败，请重试', 'danger')
                app.logger.error(f'Add post error: {e}')

    # GET 请求，渲染表单
    categories = Category.query.all()
    tags = Tag.query.all()
    return render_template('admin/post_edit.html',
                         categories=categories,
                         tags=tags,
                         post=None)


@app.route('/admin/post/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def admin_post_edit(post_id):
    """
    编辑文章
    """
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form.get('title', '').strip()
        post.content = request.form.get('content', '').strip()
        post.summary = request.form.get('summary', '').strip() or None
        post.category_id = request.form.get('category_id', type=int)
        post.is_published = request.form.get('is_published') == 'on'

        # 更新标签
        tag_ids = request.form.getlist('tags', type=int)
        post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

        try:
            db.session.commit()
            flash('文章更新成功！', 'success')
            return redirect(url_for('admin_posts'))
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请重试', 'danger')
            app.logger.error(f'Edit post error: {e}')

    # GET 请求，渲染表单
    categories = Category.query.all()
    tags = Tag.query.all()
    return render_template('admin/post_edit.html',
                         categories=categories,
                         tags=tags,
                         post=post)


@app.route('/admin/post/delete/<int:post_id>', methods=['POST'])
@login_required
def admin_post_delete(post_id):
    """
    删除文章
    """
    post = Post.query.get_or_404(post_id)

    try:
        db.session.delete(post)
        db.session.commit()
        flash('文章删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash('删除失败', 'danger')
        app.logger.error(f'Delete post error: {e}')

    return redirect(url_for('admin_posts'))


# ==================== 分类管理路由 ====================

@app.route('/admin/categories')
@login_required
def admin_categories():
    """
    分类管理页面
    """
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)


@app.route('/admin/category/add', methods=['POST'])
@login_required
def admin_category_add():
    """
    添加分类
    """
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('分类名称不能为空', 'danger')
        return redirect(url_for('admin_categories'))

    # 检查分类名是否已存在
    if Category.query.filter_by(name=name).first():
        flash('分类名称已存在', 'danger')
        return redirect(url_for('admin_categories'))

    category = Category(name=name, description=description)

    try:
        db.session.add(category)
        db.session.commit()
        flash('分类添加成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash('添加失败', 'danger')
        app.logger.error(f'Add category error: {e}')

    return redirect(url_for('admin_categories'))


@app.route('/admin/category/edit/<int:category_id>', methods=['POST'])
@login_required
def admin_category_edit(category_id):
    """
    编辑分类
    """
    category = Category.query.get_or_404(category_id)

    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('分类名称不能为空', 'danger')
        return redirect(url_for('admin_categories'))

    # 检查新名称是否与其他分类冲突
    existing = Category.query.filter(
        Category.name == name,
        Category.id != category_id
    ).first()

    if existing:
        flash('分类名称已存在', 'danger')
        return redirect(url_for('admin_categories'))

    category.name = name
    category.description = description

    try:
        db.session.commit()
        flash('分类更新成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash('更新失败', 'danger')
        app.logger.error(f'Edit category error: {e}')

    return redirect(url_for('admin_categories'))


@app.route('/admin/category/delete/<int:category_id>', methods=['POST'])
@login_required
def admin_category_delete(category_id):
    """
    删除分类
    注意：如果该分类下有文章，则不能删除
    """
    category = Category.query.get_or_404(category_id)

    # 检查是否有文章使用此分类
    if category.posts.count() > 0:
        flash('该分类下还有文章，无法删除', 'danger')
        return redirect(url_for('admin_categories'))

    try:
        db.session.delete(category)
        db.session.commit()
        flash('分类删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash('删除失败', 'danger')
        app.logger.error(f'Delete category error: {e}')

    return redirect(url_for('admin_categories'))


# ==================== 标签管理路由 ====================

@app.route('/admin/tags')
@login_required
def admin_tags():
    """
    标签管理页面
    """
    tags = Tag.query.all()
    return render_template('admin/tags.html', tags=tags)


@app.route('/admin/tag/add', methods=['POST'])
@login_required
def admin_tag_add():
    """
    添加标签
    """
    name = request.form.get('name', '').strip()

    if not name:
        flash('标签名称不能为空', 'danger')
        return redirect(url_for('admin_tags'))

    # 检查标签名是否已存在
    if Tag.query.filter_by(name=name).first():
        flash('标签名称已存在', 'danger')
        return redirect(url_for('admin_tags'))

    tag = Tag(name=name)

    try:
        db.session.add(tag)
        db.session.commit()
        flash('标签添加成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash('添加失败', 'danger')
        app.logger.error(f'Add tag error: {e}')

    return redirect(url_for('admin_tags'))


@app.route('/admin/tag/edit/<int:tag_id>', methods=['POST'])
@login_required
def admin_tag_edit(tag_id):
    """
    编辑标签
    """
    tag = Tag.query.get_or_404(tag_id)

    name = request.form.get('name', '').strip()

    if not name:
        flash('标签名称不能为空', 'danger')
        return redirect(url_for('admin_tags'))

    # 检查新名称是否与其他标签冲突
    existing = Tag.query.filter(Tag.name == name, Tag.id != tag_id).first()
    if existing:
        flash('标签名称已存在', 'danger')
        return redirect(url_for('admin_tags'))

    tag.name = name

    try:
        db.session.commit()
        flash('标签更新成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash('更新失败', 'danger')
        app.logger.error(f'Edit tag error: {e}')

    return redirect(url_for('admin_tags'))


@app.route('/admin/tag/delete/<int:tag_id>', methods=['POST'])
@login_required
def admin_tag_delete(tag_id):
    """
    删除标签
    """
    tag = Tag.query.get_or_404(tag_id)

    try:
        db.session.delete(tag)
        db.session.commit()
        flash('标签删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash('删除失败', 'danger')
        app.logger.error(f'Delete tag error: {e}')

    return redirect(url_for('admin_tags'))


# ==================== 评论管理路由 ====================

@app.route('/admin/comments')
@login_required
def admin_comments():
    """
    评论管理页面
    """
    page = request.args.get('page', 1, type=int)

    pagination = Comment.query.order_by(Comment.created_at.desc()).paginate(
        page=page,
        per_page=app.config['ADMIN_PER_PAGE'],
        error_out=False
    )

    return render_template('admin/comments.html',
                         comments=pagination.items,
                         pagination=pagination)


@app.route('/admin/comment/delete/<int:comment_id>', methods=['POST'])
@login_required
def admin_comment_delete(comment_id):
    """
    删除评论
    """
    comment = Comment.query.get_or_404(comment_id)

    try:
        db.session.delete(comment)
        db.session.commit()
        flash('评论删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash('删除失败', 'danger')
        app.logger.error(f'Delete comment error: {e}')

    return redirect(url_for('admin_comments'))


# ==================== 程序入口 ====================

if __name__ == '__main__':
    # 确保数据库表已创建
    with app.app_context():
        db.create_all()
        print("数据库表已创建/更新完成")

        # 创建默认数据（如果需要）
        from models import create_default_data
        create_default_data(app)

    # 启动开发服务器
    # debug=True: 开启调试模式，代码修改后自动重载
    # host='0.0.0.0': 允许外部访问
    # port=5000: 默认端口
    app.run(debug=True, host='0.0.0.0', port=5000)