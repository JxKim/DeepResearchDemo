import psycopg


def drop_db_and_user():
    """删除数据库和用户"""
    try:
        # 连接到默认数据库
        with psycopg.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="abc123456",
            dbname="postgres"
        ) as conn:
            # 设置自动提交
            conn.autocommit = True
            
            with conn.cursor() as cursor:
                # 先断开所有连接到smartagent_db的会话
                cursor.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'smartagent_db';")
                print("断开所有连接到smartagent_db的会话成功")
                
                # 删除数据库
                cursor.execute("DROP DATABASE IF EXISTS smartagent_db;")
                print("删除数据库 smartagent_db 成功")
                
                # 删除用户
                cursor.execute("DROP USER IF EXISTS smartagent_user;")
                print("删除用户 smartagent_user 成功")
        
        return True
    except psycopg.Error as e:
        print(f"删除数据库和用户失败: {e}")
        return False


if __name__ == "__main__":
    print("开始删除数据库和用户...")
    success = drop_db_and_user()
    if success:
        print("数据库和用户删除成功！")
    else:
        print("数据库和用户删除失败！")
