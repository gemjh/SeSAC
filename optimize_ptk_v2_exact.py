import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import warnings
warnings.filterwarnings('ignore')

# 필요한 라이브러리들
import librosa
import scipy.signal
from pydub import AudioSegment

def convert_audio_for_model_exact(user_file, output_file=None, EXPECTED_SAMPLE_RATE=16000):
    """원본과 정확히 동일한 오디오 변환"""
    import tempfile
    import uuid
    
    if output_file is None:
        output_file = os.path.join(tempfile.gettempdir(), f"converted_audio_{uuid.uuid4().hex}.wav")
    
    audio = AudioSegment.from_file(user_file)
    audio = audio.set_frame_rate(EXPECTED_SAMPLE_RATE).set_channels(1)
    audio.export(output_file, format="wav")
    return output_file

def count_peaks_exact_match(filepath, height=0.05, distance=3000, plot=False):
    """원본 ptk_sound.py와 정확히 동일한 구현"""
    temp_file = None
    try:
        temp_file = convert_audio_for_model_exact(filepath)
        y, sr = librosa.load(temp_file, sr=None)  # 원본과 동일하게 sr=None
        # n초 (원본과 동일)
        y_trimmed = y[:sr * 3]

        y_trimmed = y_trimmed / np.max(np.abs(y_trimmed))

        # 피크 탐지 (원본과 동일)
        peaks, _ = scipy.signal.find_peaks(y_trimmed, height=height, distance=distance)

        if plot:
            plt.figure(figsize=(12, 4))
            plt.plot(y_trimmed)
            plt.plot(peaks, y_trimmed[peaks], "rx")  # 피크 위치 표시
            plt.title(f"Detected Peaks: {len(peaks)}")
            plt.show()

        return len(peaks)
    except Exception as e:
        print(f"⚠️ 파일 처리 오류 {filepath}: {e}")
        return 0
    finally:
        # 임시 파일 정리
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass

def optimize_ptk_exact():
    """원본과 정확히 동일한 방식으로 PTK 파라미터 최적화"""
    print("🔍 PTK 파라미터 최적화 (원본 정확 매치)...")
    
    # 원본 파라미터를 포함한 범위
    height_values = np.array([0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06, 0.065, 0.07])  # 0.05 포함
    distance_values = np.array([2500, 2750, 3000, 3250, 3500])  # 3000 포함
    
    print(f"📊 테스트할 조합 수: {len(height_values) * len(distance_values)}")
    print(f"📌 원본 파라미터 포함: height=0.05, distance=3000")
    
    # 데이터 로드 (원본과 동일)
    folder = r'C:\Users\user\Downloads\data'
    pattern = os.path.join(folder, '**', 'CLAP_D', '1', 'p*.wav')
    wav_files = glob.glob(pattern, recursive=True)
    print(f"🎵 발견된 WAV 파일 수: {len(wav_files)}")
    
    # 라벨 데이터 로드 (원본과 동일)
    df = pd.read_csv(r'H:\labeled_data_D.csv', header=1, index_col=0)
    ptk_label = df.loc[:, ['peo_2nd', 'teo_2nd', 'keo_2nd', 'ptk_2nd']]
    
    optimization_results = []
    total_combinations = len(height_values) * len(distance_values)
    combination_count = 0
    
    print("🚀 최적화 시작...")
    
    for height in height_values:
        for distance in distance_values:
            combination_count += 1
            
            is_original = (height == 0.05 and distance == 3000)
            marker = "🎯" if is_original else "📈"
            
            print(f"\n{marker} 진행률: {combination_count}/{total_combinations} "
                  f"({combination_count/total_combinations*100:.1f}%)")
            print(f"🎯 현재 테스트: height={height:.3f}, distance={int(distance)}" + 
                  (" ⭐ 원본 파라미터" if is_original else ""))
            
            try:
                start_time = time.time()
                
                # 원본과 정확히 동일한 DataFrame 구조
                ptk_result = pd.DataFrame(columns=['peo_2nd', 'teo_2nd', 'keo_2nd', 'ptk_2nd'])
                
                for wav_file in wav_files:
                    # 원본과 동일한 경로 파싱
                    parts = wav_file.replace(folder, '').strip(os.sep).split(os.sep)
                    if len(parts) > 0:
                        index_key = parts[0]
                    else:
                        index_key = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(wav_file))))
                    
                    # 원본과 동일한 DataFrame 인덱스 처리
                    if index_key not in ptk_result.index:
                        ptk_result.loc[index_key] = [None, None, None, None]
                    
                    filename = os.path.basename(wav_file)
                    
                    # 원본과 정확히 동일한 로직
                    if 'p_2_' in filename:
                        result = count_peaks_exact_match(wav_file, height=height, distance=distance)
                        ptk_result.loc[index_key, 'peo_2nd'] = result
                    elif 'p_5_' in filename:
                        result = count_peaks_exact_match(wav_file, height=height, distance=distance)
                        ptk_result.loc[index_key, 'teo_2nd'] = result
                    elif 'p_8_' in filename:
                        result = count_peaks_exact_match(wav_file, height=height, distance=distance)
                        ptk_result.loc[index_key, 'keo_2nd'] = result
                    elif 'p_11_' in filename:
                        result = count_peaks_exact_match(wav_file, height=height, distance=distance)
                        ptk_result.loc[index_key, 'ptk_2nd'] = round(result/3, 1)
                
                # 원본과 정확히 동일한 상관계수 계산
                ptk_result.index = ptk_result.index.astype(int)
                correlation_results = {}
                
                for col in ptk_result.columns:
                    if col in ptk_label.columns:
                        # 원본과 동일한 방식
                        temp_combined = pd.concat([ptk_result[col], ptk_label[col]], axis=1, join="inner").dropna()
                        if not temp_combined.empty:
                            correlation = temp_combined.corr(method='pearson').iloc[0, 1]
                            correlation_results[col] = correlation
                        else:
                            correlation_results[col] = None
                
                # None 값 제외하고 평균/최대 계산
                valid_correlations = {k: v for k, v in correlation_results.items() if v is not None}
                if not valid_correlations:
                    continue
                
                avg_correlation = np.mean(list(valid_correlations.values()))
                max_correlation = max(valid_correlations.values())
                
                elapsed_time = time.time() - start_time
                
                result_entry = {
                    'height': height,
                    'distance': distance,
                    'avg_correlation': avg_correlation,
                    'max_correlation': max_correlation,
                    'elapsed_time': elapsed_time,
                    'is_original': is_original
                }
                
                # 각 열별 상관계수 저장
                for col, corr in correlation_results.items():
                    result_entry[f'{col}_correlation'] = corr if corr is not None else 0
                
                optimization_results.append(result_entry)
                
                result_str = f"✅ 평균: {avg_correlation:.6f}, 최대: {max_correlation:.6f}"
                if is_original:
                    result_str += " ⭐ 원본 결과!"
                print(result_str)
                
                # 원본 파라미터 결과 상세 출력
                if is_original:
                    print("🔍 원본 파라미터 상세 결과:")
                    for col, corr in correlation_results.items():
                        if corr is not None:
                            print(f"   {col}: {corr:.6f}")
                
            except Exception as e:
                print(f"❌ 오류: {e}")
                continue
    
    # 결과 처리
    results_df = pd.DataFrame(optimization_results)
    if results_df.empty:
        return None, None, None
    
    results_df.to_csv('H:/ptk_optimization_exact.csv', index=False)
    
    # 원본 파라미터 결과
    original_result = results_df[results_df['is_original'] == True]
    
    best_avg = results_df.loc[results_df['avg_correlation'].idxmax()]
    best_max = results_df.loc[results_df['max_correlation'].idxmax()]
    
    print("\n🏆 최적화 결과 (원본 정확 매치):")
    print("="*70)
    
    if not original_result.empty:
        orig = original_result.iloc[0]
        print(f"⭐ 원본 파라미터 결과:")
        print(f"   평균 상관계수: {orig['avg_correlation']:.6f}")
        print(f"   최대 상관계수: {orig['max_correlation']:.6f}")
        print("   개별 상관계수:")
        for col in ['peo_2nd', 'teo_2nd', 'keo_2nd', 'ptk_2nd']:
            if f'{col}_correlation' in orig and orig[f'{col}_correlation'] is not None:
                print(f"     {col}: {orig[f'{col}_correlation']:.6f}")
        print("")
    
    print(f"🏆 최고 평균 상관계수: {best_avg['avg_correlation']:.6f}")
    print(f"   최적 height: {best_avg['height']:.3f}")
    print(f"   최적 distance: {int(best_avg['distance'])}")
    
    improvement = ((best_avg['avg_correlation'] - orig['avg_correlation']) / orig['avg_correlation'] * 100 
                  if not original_result.empty and orig['avg_correlation'] > 0 else 0)
    if improvement > 0:
        print(f"   개선율: +{improvement:.2f}%")
    
    print("\n🎯 개별 열별 최고 상관계수:")
    for col in ['peo_2nd', 'teo_2nd', 'keo_2nd', 'ptk_2nd']:
        if f'{col}_correlation' in best_avg:
            print(f"   {col}: {best_avg[f'{col}_correlation']:.6f}")
    print("="*70)
    
    return results_df, best_avg, best_max

if __name__ == "__main__":
    result = optimize_ptk_exact()
    if result[0] is not None:
        print("💾 원본 정확 매치 방식 결과 저장 완료!")
    else:
        print("❌ 원본 정확 매치 방식 실패")