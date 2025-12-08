import psycopg


def create_db_and_user():
    """创建数据库和用户"""
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
                # 创建用户
                cursor.execute("CREATE USER smartagent_user WITH PASSWORD 'smartagent_pass';")
                print("创建用户 smartagent_user 成功")
                
                # 创建数据库
                cursor.execute("CREATE DATABASE smartagent_db;")
                print("创建数据库 smartagent_db 成功")
                
                # 授予权限
                cursor.execute("GRANT ALL PRIVILEGES ON DATABASE smartagent_db TO smartagent_user;")
                print("授予数据库权限成功")
                
                # 连接到新创建的数据库，授予模式权限
                conn_new = psycopg.connect(
                    host="localhost",
                    port="5432",
                    user="postgres",
                    password="abc123456",
                    dbname="smartagent_db"
                )
                conn_new.autocommit = True
                
                with conn_new.cursor() as cursor_new:
                    # 授予对public模式的所有权限
                    cursor_new.execute("GRANT ALL PRIVILEGES ON SCHEMA public TO smartagent_user;")
                    print("授予模式权限成功")
                    
                    # 授予创建类型的权限
                    cursor_new.execute("GRANT CREATE ON DATABASE smartagent_db TO smartagent_user;")
                    print("授予创建类型权限成功")
                
                conn_new.close()
        
        return True
    except psycopg.Error as e:
        print(f"创建数据库和用户失败: {e}")
        return False


if __name__ == "__main__":
    print("开始创建数据库和用户...")
    success = create_db_and_user()
    if success:
        print("数据库和用户创建成功！")
    else:
        print("数据库和用户创建失败！")
