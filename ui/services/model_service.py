# ============================================================================
# 개별 모듈 lazy loading으로 변경 - 2025.08.22 수정
# 필요할 때만 각 모듈을 import하여 메모리 효율성 개선
# ============================================================================
import time
from pathlib import Path
import sys

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

# 모델링하고 결과 딕셔너리 반환
def model_process(path_info):  
    try:          
        # 세션으로부터 파일 경로와 목록 정보를 조회
        ret = path_info[['MAIN_PATH','SUB_PATH','FILE_NAME']]

        ah_sound_path=[]
        ptk_sound_path=[]
        ltn_rpt_path=[]
        guess_end_path=[]
        say_ani_path=[]
        say_obj_path=[]
        talk_clean_path=[]
        talk_pic_path=[]

        ah_sound_result=None
        p_sound_result=None
        t_sound_result=None
        k_sound_result=None
        ptk_sound_result=None
        ltn_rpt_result=None
        guess_end_result=None
        say_ani_result=None
        say_obj_result=None
        talk_clean_result=None
        talk_pic_result=None

        # 폴더 구조대로 순서 배열
        a_path_list=[ltn_rpt_path,guess_end_path,say_obj_path,say_ani_path,talk_pic_path]
        d_path_list=[ah_sound_path,ptk_sound_path,talk_clean_path]

        # 경로 조회 및 재구성
        for i in range(len(ret)):
            main_path = str(ret.loc[i, 'MAIN_PATH'])
            sub_path = str(ret.loc[i, 'SUB_PATH'])
            filename = str(ret.loc[i, 'FILE_NAME'])

            # windows인 경우 따로 처리 필요
            if sys.platform.startswith('win'):
                sub_path.replace('/','\\')
            
            # base_path 기준으로 경로 구성: base_path / upload / files / main_path / sub_path / filename
            from dotenv import load_dotenv
            from pathlib import Path as EnvPath
            import os
            env_path = EnvPath(__file__).parent.parent.parent / ".env"
            load_dotenv(dotenv_path=env_path)
            base_path = os.getenv("base_path")
            
            file_path = os.path.join(base_path, 'files','upload', main_path, sub_path.upper(), filename)


            # 필요하다면 문자열로 변환
            file_path = str(file_path)
            # 파일 존재 여부 확인
            # if not os.path.exists(file_path):
            #     # st.warning(f"❌ 파일 없음: {file_path}")
            #     continue
                
            sub_path_parts = Path(sub_path).parts
            # d일 때
            if sub_path_parts[0].lower() == 'clap_d':
                for i in range(3):
                    if sub_path_parts[1] == str(i):
                        d_path_list[i].append(file_path)
                        
            # a일 때
            elif sub_path_parts[0].lower() == 'clap_a':
                for i in range(5):
                    if sub_path_parts[1] == str(i+3):
                        a_path_list[i].append(file_path)

        # ============================================================================
        # 결과 딕셔너리로 저장 - 2025.08.22 수정
        # 필요할 때만 API import - 2025.08.22 수정
        # ============================================================================  
        fin_scores={}                
        if len(ltn_rpt_path)>0:
            start_time = time.time()
            try:
                ltn_rpt = get_ltn_rpt()
                ltn_rpt_result=ltn_rpt.predict_score(ltn_rpt_path)
                fin_scores['LTN_RPT']=int(ltn_rpt_result)
                print(f"LTN_RPT 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"LTN_RPT 모델 실행 중 오류 발생: {e}")
                fin_scores['LTN_RPT'] = 0

        if len(guess_end_path)>0:
            start_time = time.time()
            # from ui.utils.env_utils import model_common_path
            try:
                guess_end = get_guess_end()
                temp=[]
                # infer = guess_end.GuessEndInferencer(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models", "guess_end_model.keras"))
                for idx,p in enumerate(guess_end_path):
                    temp.append(guess_end.predict_guess_end_score(p,idx))
                guess_end_result=sum(temp)
                # print('--------------\n\n\n',guess_end_result,idx,'\n\n\n----------------------')


                fin_scores['GUESS_END']=int(guess_end_result)
                print(f"GUESS_END 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"GUESS_END 모델 실행 중 오류 발생: {e}")
                fin_scores['GUESS_END'] = 0

        if len(say_obj_path)>0:
            start_time = time.time()
            try:
                say_obj = get_say_obj()
                say_obj_result=say_obj.predict_say_object_total(say_obj_path[5],say_obj_path[8])  
                fin_scores['SAY_OBJ']=int(say_obj_result)
                print(f"SAY_OBJ 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"SAY_OBJ 모델 실행 중 오류 발생: {e}")
                fin_scores['SAY_OBJ'] = 0
            
        if len(say_ani_path)>0:
            start_time = time.time()
            try:
                say_ani = get_say_ani()
                say_ani_result=say_ani.score_audio(say_ani_path[0])
                fin_scores['SAY_ANI']=int(say_ani_result)
                print(f"SAY_ANI 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"SAY_ANI 모델 실행 중 오류 발생: {e}")
                fin_scores['SAY_ANI'] = 0
            
        if len(talk_pic_path)>0:
            start_time = time.time()
            try:
                talk_pic = get_talk_pic()
                talk_pic_result=talk_pic.score_audio(talk_pic_path[0])
                fin_scores['TALK_PIC']=int(talk_pic_result)
                print(f"TALK_PIC 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"TALK_PIC 모델 실행 중 오류 발생: {e}")
                fin_scores['TALK_PIC'] = 0
            
        if len(ah_sound_path)>0:
            start_time = time.time()
            try:
                ah_sound = get_ah_sound()
                ah_sound_result=round(ah_sound.analyze_pitch_stability(ah_sound_path[0]),2)
                fin_scores['AH_SOUND']=ah_sound_result
                print(f"AH_SOUND 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"AH_SOUND 모델 실행 중 오류 발생: {e}")
                fin_scores['AH_SOUND'] = 0

        if len(ptk_sound_path)>0:
            start_time = time.time()
            try:
                ptk_sound = get_ptk_sound()
                temp_p,temp_t,temp_k,temp_ptk=[],[],[],[]
                for i in range(len(ptk_sound_path)):
                    if i < 3:
                        temp_p.append(ptk_sound.ptk_each(ptk_sound_path[i]))
                    elif i < 6:
                        temp_t.append(ptk_sound.ptk_each(ptk_sound_path[i]))
                    elif i < 9:
                        temp_k.append(ptk_sound.ptk_each(ptk_sound_path[i]))
                    elif i < 12:
                        temp_ptk.append(ptk_sound.ptk_whole(ptk_sound_path[i]))

                if temp_p:
                    fin_scores['P_SOUND']=round(max(temp_p), 2)
                if temp_t:
                    fin_scores['T_SOUND']=round(max(temp_t), 2)
                if temp_k:
                    fin_scores['K_SOUND']=round(max(temp_k), 2)
                if temp_ptk:
                    fin_scores['PTK_SOUND']=round(max(temp_ptk), 2)
                print(f"PTK_SOUND 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"PTK_SOUND 모델 실행 중 오류 발생: {e}")
                fin_scores['P_SOUND'] = 0
                fin_scores['T_SOUND'] = 0
                fin_scores['K_SOUND'] = 0
                fin_scores['PTK_SOUND'] = 0

        if len(talk_clean_path)>0:
            start_time = time.time()
            try:
                talk_clean = get_talk_clean()
                talk_clean_result=talk_clean.main(talk_clean_path)
                fin_scores['TALK_CLEAN']=int(talk_clean_result)
                print(f"TALK_CLEAN 모델 실행 시간: {time.time() - start_time:.2f}초")
            except Exception as e:
                print(f"TALK_CLEAN 모델 실행 중 오류 발생: {e}")
                fin_scores['TALK_CLEAN'] = 0

        # ['PATIENT_ID', 'ORDER_NUM', 'ASSESS_TYPE', 'QUESTION_CD', 'QUESTION_NO', 'QUESTION_MINOR_NO', 'SCORE']
        # fin_scores = {
        #     'LTN_RPT':ltn_rpt_result,
        #     'GUESS_END':guess_end_result,
        #     'SAY_OBJ':say_obj_result,
        #     'SAY_ANI':say_ani_result,
        #     'TALK_PIC':talk_pic_result,
        #     'AH_SOUND':ah_sound_result,
        #     'P_SOUND':ptk_sound_result[0],
        #     'T_SOUND':ptk_sound_result[1],
        #     'K_SOUND':ptk_sound_result[2],
        #     'PTK_SOUND':ptk_sound_result[3],
        #     'TALK_CLEAN':talk_clean_result
        # }
        return fin_scores

    except Exception as e:
        print(f"모델링 중 오류 발생: {e}")
        raise