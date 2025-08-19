# 간단한 인증 함수
def authenticate_user(user_id, password):
    if user_id == "user" and password == 'd':
        return True
        
    return False