"""
Flask 博客系统 - 数据库初始化脚本
用于初始化数据库结构和默认数据

使用方法:
    python init_db.py
"""

import os
import sys

# 添加当前目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app import create_app
from models import db, init_db, create_default_data


def main():
    """
    主函数：初始化数据库
    """
    print("=" * 50)
    print("Flask 博客系统 - 数据库初始化工具")
    print("=" * 50)

    # 创建应用实例
    app = create_app('development')

    with app.app_context():
        # 检查数据库文件是否存在
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

        if os.path.exists(db_path):
            print(f"\n⚠️  警告：数据库文件已存在 ({db_path})")
            response = input("是否重新创建？这将删除所有现有数据！(y/N): ")

            if response.lower() == 'y':
                # 删除现有数据库
                try:
                    os.remove(db_path)
                    print("✅ 已删除旧数据库")
                except Exception as e:
                    print(f"❌ 删除数据库失败: {e}")
                    return
            else:
                print("\n⏭️  跳过数据库创建")
                return

        print("\n🔄 正在创建数据库表...")

        try:
            # 创建所有表
            init_db(app)
            print("✅ 数据库表创建成功！")

            # 创建默认数据
            print("\n🔄 正在创建默认数据...")
            create_default_data(app)
            print("✅ 默认数据创建成功！")

            print("\n" + "=" * 50)
            print("🎉 数据库初始化完成！")
            print("=" * 50)
            print("\n📋 默认管理员账号：")
            print(f"   用户名: {app.config['DEFAULT_ADMIN_USERNAME']}")
            print(f"   密码: {app.config['DEFAULT_ADMIN_PASSWORD']}")
            print("\n⚠️  请及时修改默认密码！")
            print("\n🚀 启动应用：python app.py")
            print("🌐 访问地址：http://localhost:5000")
            print("=" * 50)

        except Exception as e:
            print(f"\n❌ 初始化失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
