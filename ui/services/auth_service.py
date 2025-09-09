# 간단한 인증 함수
def authenticate_user(user_id, password):
    if user_id == "SeSAC" and password == '1234':
        return True
        
    return False