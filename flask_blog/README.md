# Flask 个人博客系统

一个基于 Python Flask 框架开发的个人博客系统，功能完善、代码结构清晰、易于扩展。

## 🚀 功能特性

### 前台功能
- ✅ 文章列表展示（分页、标题、摘要、发布时间）
- ✅ 文章详情页（支持 HTML 内容、浏览统计）
- ✅ 分类浏览（按分类筛选文章）
- ✅ 标签云（标签聚合、按标签筛选）
- ✅ 文章搜索（按标题和内容关键词搜索）
- ✅ 评论功能（访客可发表评论，无需审核）
- ✅ 响应式设计（适配手机、平板、电脑）

### 后台管理
- ✅ 管理员登录（Session 认证）
- ✅ 仪表盘（数据统计、快捷操作）
- ✅ 文章管理（增删改查、草稿/发布状态）
- ✅ 分类管理（增删改查）
- ✅ 标签管理（增删改查）
- ✅ 评论管理（查看、删除）

## 🛠️ 技术栈

- **后端框架**: Python 3.9+ + Flask 2.0+
- **数据库**: SQLite3 + SQLAlchemy ORM
- **前端框架**: HTML5 + CSS3 + Bootstrap 5
- **图标库**: Bootstrap Icons

## 📁 项目结构

```
flask_blog/
├── app.py                 # 主程序入口
├── config.py              # 配置文件
├── models.py              # 数据模型定义
├── init_db.py             # 数据库初始化脚本
├── requirements.txt       # pip 依赖包列表
├── environment.yml        # Conda 环境配置文件
├── README.md              # 项目说明文档
├── blog.db                # SQLite 数据库文件（运行时生成）
├── static/                # 静态文件目录
│   ├── css/
│   │   └── style.css      # 自定义样式
│   └── js/
│       └── main.js        # 前端交互脚本
└── templates/             # HTML 模板目录
    ├── base.html          # 前台基础模板
    ├── index.html         # 首页（文章列表）
    ├── post.html          # 文章详情页
    ├── category.html      # 分类文章页
    ├── tag.html           # 标签文章页
    ├── search.html        # 搜索结果页
    ├── errors/            # 错误页面
    │   ├── 404.html
    │   └── 500.html
    └── admin/             # 后台管理模板
        ├── base.html      # 后台基础模板
        ├── login.html     # 登录页面
        ├── dashboard.html # 仪表盘
        ├── posts.html     # 文章列表
        ├── post_edit.html # 文章编辑
        ├── categories.html# 分类管理
        ├── tags.html      # 标签管理
        └── comments.html  # 评论管理
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.9 或更高版本
- pip 或 conda 包管理器

### 2. 安装依赖

#### 方式一: 使用 pip + venv（推荐）

```bash
# 进入项目目录
cd flask_blog

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

#### 方式二: 使用 Conda

```bash
# 进入项目目录
cd flask_blog

# 创建 Conda 环境（会自动安装 Python 3.9）
conda env create -f environment.yml

# 激活环境
conda activate flask_blog

# 如果修改了依赖，更新环境
conda env update -f environment.yml
```

#### 方式三: 手动使用 Conda

```bash
# 创建环境
conda create -n flask_blog python=3.9

# 激活环境
conda activate flask_blog

# 使用 pip 安装依赖（conda 中没有的部分包需用 pip）
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
python init_db.py
```

运行后会：
- 创建 SQLite 数据库文件
- 创建所有数据表
- 创建默认管理员账号
- 创建默认分类

### 4. 启动应用

```bash
python app.py
```

应用启动后访问：
- **前台首页**: http://localhost:5000
- **后台管理**: http://localhost:5000/admin

默认管理员账号：
- 用户名: `admin`
- 密码: `admin123`

⚠️ **注意**: 首次登录后请及时修改默认密码！

## ⚙️ 配置说明

编辑 `config.py` 文件可以修改以下配置：

```python
# 数据库配置
SQLALCHEMY_DATABASE_URI = 'sqlite:///blog.db'  # 数据库文件路径

# 分页配置
POSTS_PER_PAGE = 5       # 前台每页文章数
ADMIN_PER_PAGE = 10      # 后台每页数据数

# Session 配置
PERMANENT_SESSION_LIFETIME = timedelta(hours=1)  # Session 过期时间

# 管理员默认账号
DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin123'
```

## 🚀 部署到服务器

### 使用 Gunicorn（推荐）

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务（4个 worker 进程，监听 5000 端口）
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/flask_blog/static;
        expires 30d;
    }
}
```

### Docker 部署（可选）

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🔒 安全建议

1. **修改默认密码**: 首次登录后立即修改管理员密码
2. **设置强密钥**: 在生产环境的 `config.py` 中设置复杂的 `SECRET_KEY`
3. **关闭调试模式**: 生产环境设置 `DEBUG = False`
4. **使用 HTTPS**: 生产环境配置 SSL 证书
5. **定期备份**: 定期备份 `blog.db` 数据库文件

## 📝 扩展功能建议

以下是一些可以进一步扩展的功能：

1. **Markdown 编辑器**: 集成 Editor.md 或 SimpleMDE
2. **图片上传**: 添加文章配图上传功能
3. **文章置顶**: 添加文章置顶功能
4. **友情链接**: 添加友情链接管理
5. **站点配置**: 后台配置站点名称、Logo 等
6. **多用户**: 支持多个作者账号
7. **邮件通知**: 新评论邮件通知
8. **SEO 优化**: 添加 meta 标签、站点地图
9. **数据统计**: 集成百度统计或 Google Analytics

## 🐛 常见问题

### Q: 数据库文件在哪里？
A: 默认在项目根目录下的 `blog.db` 文件。

### Q: 如何修改数据库？
A: 可以直接修改 `models.py` 中的模型定义，然后删除 `blog.db` 重新运行 `init_db.py`。

### Q: 如何备份数据？
A: 直接复制 `blog.db` 文件即可，SQLite 数据库就是单个文件。

### Q: 如何添加新的管理员？
A: 可以在 Python 交互式 shell 中添加：
```python
from app import app
from models import db, Admin
with app.app_context():
    admin = Admin('newuser', 'password')
    db.session.add(admin)
    db.session.commit()
```

## 📄 许可证

MIT License - 可自由使用和修改。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，欢迎联系交流。

---

**Happy Coding! 🎉**
