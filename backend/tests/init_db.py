from database import engine, check_db_connection
from models.db_models import Base


def init_db():
    """初始化数据库，创建所有表"""
    try:
        # 检查数据库连接
        if not check_db_connection():
            print("数据库连接失败，无法初始化数据库")
            return False
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功！")
        return True
    except Exception as e:
        print(f"初始化数据库失败: {e}")
        return False


if __name__ == "__main__":
    print("开始初始化数据库...")
    success = init_db()
    if success:
        print("数据库初始化成功！")
    else:
        print("数据库初始化失败！")
