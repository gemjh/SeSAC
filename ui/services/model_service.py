# ============================================================================
# 개별 모듈 lazy loading으로 변경 - 2025.08.22 수정
# 필요할 때만 각 모듈을 import하여 메모리 효율성 개선
# ============================================================================

def get_talk_pic():
    from models import talk_pic
    return talk_pic

def get_ah_sound():
    from models import ah_sound
    return ah_sound

def get_ptk_sound():
    from models import ptk_sound
    return ptk_sound

def get_talk_clean():
    from models import talk_clean
    return talk_clean

def get_say_ani():
    from models import say_ani
    return say_ani

def get_ltn_rpt():
    from models import ltn_rpt
    return ltn_rpt

def get_say_obj():
    from models import say_obj
    return say_obj

def get_guess_end():
    from models import guess_end
    return guess_end

# 하위 호환성을 위한 기존 함수 유지 (deprecated)
def get_model_modules():
    """
    DEPRECATED: 메모리 효율성을 위해 개별 get_* 함수들을 사용하세요
    """
    from models import talk_pic, ah_sound, ptk_sound, talk_clean, say_ani, ltn_rpt, say_obj
    return talk_pic, ah_sound, ptk_sound, talk_clean, say_ani, ltn_rpt, say_obj
