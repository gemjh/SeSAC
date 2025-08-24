import os
import glob
import pandas as pd
import numpy as np
import librosa
import scipy.signal
from pydub import AudioSegment

def convert_audio_for_model(user_file, output_file='temp_converted_audio.wav', EXPECTED_SAMPLE_RATE=16000):
    """오디오 파일을 모델에 맞게 변환 (모노채널 + 정규화)"""
    audio = AudioSegment.from_file(user_file)
    audio = audio.set_frame_rate(EXPECTED_SAMPLE_RATE).set_channels(1)
    audio.export(output_file, format="wav")
    return output_file

def count_peaks_from_waveform_test(filepath, height=0.19, distance=2500, plot=False):
    """원본과 동일한 피크 카운팅 함수"""
    try:
        y, sr = librosa.load(convert_audio_for_model(filepath), sr=None)
        y_trimmed = y[:sr * 3]  # 3초 자르기
        
        if np.max(np.abs(y_trimmed)) == 0:
            return 0
            
        y_trimmed = y_trimmed / np.max(np.abs(y_trimmed))
        
        peaks, _ = scipy.signal.find_peaks(y_trimmed, height=height, distance=distance)
        
        # 임시 파일 정리
        if os.path.exists('temp_converted_audio.wav'):
            os.remove('temp_converted_audio.wav')
            
        return len(peaks)
    except Exception as e:
        print(f"⚠️ 파일 처리 오류 {filepath}: {e}")
        return 0

def test_original_parameters():
    """원본 파라미터(height=0.05, distance=3000)로 상관계수 테스트"""
    print("🔍 원본 파라미터 테스트 시작...")
    
    # 데이터 로드
    folder = r'C:\Users\user\Downloads\data'
    pattern = os.path.join(folder, '**', 'CLAP_D', '1', 'p*.wav')
    wav_files = glob.glob(pattern, recursive=True)
    print(f"🎵 발견된 WAV 파일 수: {len(wav_files)}")
    
    # 라벨 데이터 로드
    df = pd.read_csv(r'H:\labeled_data_D.csv', header=1, index_col=0)
    ptk_label = df.loc[:, ['peo_1st', 'teo_1st', 'keo_1st', 'ptk_1st']]
    
    # 결과 계산
    ptk_result = pd.DataFrame(columns=['peo_1st', 'teo_1st', 'keo_1st', 'ptk_1st'])
    
    for wav_file in wav_files:
        # Windows 경로 처리
        parts = wav_file.replace(folder, '').strip(os.sep).split(os.sep)
        if len(parts) > 0:
            index_key = parts[0]
        else:
            index_key = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(wav_file))))
        
        if index_key not in ptk_result.index:
            ptk_result.loc[index_key] = [None, None, None, None]
        
        filename = os.path.basename(wav_file)
        
        # 원본과 동일한 로직
        if 'p_2_' in filename:
            result = count_peaks_from_waveform_test(wav_file, height=0.05, distance=3000)
            ptk_result.loc[index_key, 'peo_2nd'] = result
            print(f"p_2_ 파일: {filename} -> {result}")
        elif 'p_5_' in filename:
            result = count_peaks_from_waveform_test(wav_file, height=0.05, distance=3000)
            ptk_result.loc[index_key, 'teo_2nd'] = result
            print(f"p_5_ 파일: {filename} -> {result}")
        elif 'p_8_' in filename:
            result = count_peaks_from_waveform_test(wav_file, height=0.05, distance=3000)
            ptk_result.loc[index_key, 'keo_2nd'] = result
            print(f"p_8_ 파일: {filename} -> {result}")
        elif 'p_11_' in filename:
            result = count_peaks_from_waveform_test(wav_file, height=0.05, distance=3000)
            ptk_result.loc[index_key, 'ptk_2nd'] = round(result/3, 1)
            print(f"p_11_ 파일: {filename} -> {result} -> {round(result/3, 1)}")
    
    # 상관계수 계산 - 원본과 동일한 방식
    ptk_result.index = ptk_result.index.astype(int)
    correlation_results = {}
    
    print("\n📊 상관계수 계산 결과:")
    for col in ptk_result.columns:
        if col in ptk_label.columns:
            # 원본과 동일한 방식
            temp_combined = pd.concat([ptk_result[col], ptk_label[col]], axis=1, join="inner").dropna()
            if not temp_combined.empty:
                correlation = temp_combined.corr(method='pearson').iloc[0, 1]
                correlation_results[col] = correlation
                print(f"{col}: {correlation:.6f} (샘플 수: {len(temp_combined)})")
            else:
                correlation_results[col] = None
                print(f"{col}: 데이터 없음")
    
    # 결과 출력
    correlation_df = pd.DataFrame.from_dict(correlation_results, orient='index', columns=['Pearson Correlation'])
    print("\n🏆 최종 상관계수 결과:")
    print(correlation_df)
    
    # 가장 높은 상관계수
    valid_correlations = {k: v for k, v in correlation_results.items() if v is not None}
    if valid_correlations:
        max_corr = max(valid_correlations.values())
        max_col = [k for k, v in valid_correlations.items() if v == max_corr][0]
        print(f"\n📈 최고 상관계수: {max_corr:.6f} ({max_col})")
    else:
        print("\n❌ 유효한 상관계수가 없습니다.")
    
    return correlation_results, ptk_result, ptk_label

if __name__ == "__main__":
    try:
        correlation_results, ptk_result, ptk_label = test_original_parameters()
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()