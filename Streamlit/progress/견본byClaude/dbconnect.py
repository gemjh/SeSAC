import oracledb
import mysql.connector

# MySQL 데이터베이스 연결 함수
def get_verified_connection():
    """검증된 MySQL 연결을 반환"""
    try:
        # conn: DB 커넥트 인터페이스
        # cursor: sql 작업하기 위해 필요한 인터페이스
        connection = mysql.connector.connect(
            host="localhost",
            user="testuser",
            password="00000000",
            database="CLAP",
            buffered=True
        )
        cursor = connection.cursor(buffered=True)
        # execute: 실행하기
        # fetchall: 실행결과 가져오기
        cursor.execute("SELECT 1")  
        cursor.fetchall()
        cursor.close()
        return connection
    except mysql.connector.Error as e:
        st.error(f"MySQL 데이터베이스 연결 오류: {e}")
        return None

def safe_close_connection(connection):
    """연결을 안전하게 종료"""
    if connection:
        try:
            connection.close()
        except:
            pass

# MySQL 테이블 생성 함수
def create_demo_tables():
    connection = None
    try:
        connection = get_verified_connection()
        if not connection:
            return
            
        cursor = connection.cursor(buffered=True)
        
        # 사용자 테이블 생성
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(20) UNIQUE,
                    password_hash VARCHAR(255)
                )
            """)
            cursor.fetchall()  # 결과 완전히 읽기
        except mysql.connector.DatabaseError:
            pass
        
        # 환자 테이블 생성
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    patient_id VARCHAR(20),
                    name VARCHAR(50),
                    age INT,
                    gender VARCHAR(10),
                    test_type VARCHAR(20),
                    test_date DATE,
                    requester VARCHAR(100),
                    tester VARCHAR(50),
                    status VARCHAR(20) DEFAULT '완료',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.fetchall()  # 결과 완전히 읽기
        except mysql.connector.DatabaseError:
            pass
        
        connection.commit()
        cursor.close()
        
    except mysql.connector.Error as e:
        st.error(f"테이블 생성 오류: {e}")
    finally:
        safe_close_connection(connection)

# MySQL 샘플 데이터 삽입 함수
def insert_demo_data():
    connection = None
    try:
        connection = get_verified_connection()
        if not connection:
            return
            
        cursor = connection.cursor(buffered=True)
        
        # 사용자 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            password_hash = hashlib.md5("demo123".encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (user_id, password_hash)
                VALUES (%s, %s)
            """, ("user", password_hash))
            
            # 샘플 리포트 추가
            cursor.execute("""
                INSERT INTO patients (patient_id, name, age, gender, test_type, test_date, requester, tester)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, ("01258472", "박충북", 65, "남", "CLAP-D", "2024-10-16", "충북대병원(RM) / 공현호", "백동재"))
            
            connection.commit()
        
        cursor.close()

    except mysql.connector.Error as e:
        st.error(f"샘플 데이터 삽입 오류: {e}")
    finally:
        safe_close_connection(connection)

# Oracle 데이터베이스 연결 함수
def get_verified_connection():
    """검증된 Oracle 연결을 반환"""
    try:
        connection = oracledb.connect(
            user="system",
            password="oracle", 
            dsn="localhost:1521/XE"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        cursor.close()
        return connection
    except oracledb.Error as e:
        st.error(f"Oracle 데이터베이스 연결 오류: {e}")
        return None

def safe_close_connection(connection):
    """연결을 안전하게 종료"""
    if connection:
        try:
            connection.close()
        except:
            pass

# Oracle 테이블 생성 함수
def create_demo_tables():
    connection = None
    try:
        connection = get_verified_connection()
        if not connection:
            return
            
        cursor = connection.cursor()
        
        # 시퀀스 생성
        sequences = [
            "CREATE SEQUENCE users_seq START WITH 1 INCREMENT BY 1 NOCACHE",
            "CREATE SEQUENCE patients_seq START WITH 1 INCREMENT BY 1 NOCACHE"
        ]
        
        for seq_sql in sequences:
            try:
                cursor.execute(seq_sql)
            except oracledb.DatabaseError:
                pass
        
        # 사용자 테이블 생성
        try:
            cursor.execute("""
                CREATE TABLE users (
                    id NUMBER PRIMARY KEY,
                    user_id VARCHAR2(20) UNIQUE,
                    password_hash VARCHAR2(255)
                )
            """)
        except oracledb.DatabaseError:
            pass
        
        # 환자 테이블 생성
        try:
            cursor.execute("""
                CREATE TABLE patients (
                    id NUMBER PRIMARY KEY,
                    patient_id VARCHAR2(20),
                    name VARCHAR2(50),
                    age NUMBER,
                    gender VARCHAR2(10),
                    test_type VARCHAR2(20),
                    test_date DATE,
                    requester VARCHAR2(100),
                    tester VARCHAR2(50),
                    created_at DATE DEFAULT SYSDATE
                )
            """)
        except oracledb.DatabaseError:
            pass
        
        connection.commit()
        
    except oracledb.Error as e:
        st.error(f"테이블 생성 오류: {e}")
    finally:
        safe_close_connection(connection)

# Oracle 샘플 데이터 삽입 함수
def insert_demo_data():
    connection = None
    try:
        connection = get_verified_connection()
        if not connection:
            return
            
        cursor = connection.cursor()
        
        # 사용자 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            password_hash = hashlib.md5("demo123".encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (id, user_id, password_hash)
                VALUES (users_seq.NEXTVAL, :1, :2)
            """, ("user", password_hash))
            
            # 샘플 리포트 추가
            for i in range(5):
                cursor.execute("""
                    INSERT INTO patients (id, patient_id, name, age, gender, test_type, test_date, requester, tester)
                    VALUES (reports_seq.NEXTVAL, :1, :2, :3,:4,:5, TO_DATE(:6, 'YYYY-MM-DD'), :7, :8)
                """, ("01258472","박충북",65, "남","CLAP-D", "2024-10-16", "충북대병원(RM) / 공현호", "백동재"))
            
            connection.commit()
            
    except oracledb.Error as e:
        st.error(f"샘플 데이터 삽입 오류: {e}")
    finally:
        safe_close_connection(connection)