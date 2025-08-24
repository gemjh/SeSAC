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

def count_peaks_direct_load(filepath, height=0.05, distance=3000, plot=False):
    """
    전처리 없이 원본 파일을 직접 로드하는 방식
    """
    try:
        # 직접 librosa로 로드 (16kHz 모노채널로 변환)
        y, sr = librosa.load(filepath, sr=16000, mono=True)
        # 3초 자르기
        y_trimmed = y[:sr * 3]
        
        if len(y_trimmed) == 0 or np.max(np.abs(y_trimmed)) == 0:
            return 0
            
        # 정규화
        y_trimmed = y_trimmed / np.max(np.abs(y_trimmed))
        
        # 피크 탐지
        peaks, _ = scipy.signal.find_peaks(y_trimmed, height=height, distance=distance)
        
        if plot:
            plt.figure(figsize=(12, 4))
            plt.plot(y_trimmed)
            plt.plot(peaks, y_trimmed[peaks], "rx")
            plt.title(f"Detected Peaks: {len(peaks)}")
            plt.show()
            
        return len(peaks)
    except Exception as e:
        print(f"⚠️ 파일 처리 오류 {filepath}: {e}")
        return 0

def optimize_ptk_direct():
    """
    직접 로드 방식으로 PTK 파라미터 최적화
    """
    print("🔍 PTK 파라미터 최적화 (직접 로드 방식)...")
    
    # 원본 파라미터 주변에서 세밀하게
    height_values = np.arange(0.03, 0.08, 0.005)  # 0.05 주변
    distance_values = np.arange(2500, 3500, 100)  # 3000 주변
    
    print(f"📊 테스트할 조합 수: {len(height_values) * len(distance_values)}")
    
    # 데이터 로드
    folder = r'C:\Users\user\Downloads\data'
    pattern = os.path.join(folder, '**', 'CLAP_D', '1', 'p*.wav')
    wav_files = glob.glob(pattern, recursive=True)
    print(f"🎵 발견된 WAV 파일 수: {len(wav_files)}")
    
    # 라벨 데이터 로드
    df = pd.read_csv(r'H:\labeled_data_D.csv', header=1, index_col=0)
    ptk_label = df.loc[:, ['peo_2nd', 'teo_2nd', 'keo_2nd', 'ptk_2nd']]
    
    optimization_results = []
    total_combinations = len(height_values) * len(distance_values)
    combination_count = 0
    
    print("🚀 최적화 시작...")
    
    for height in height_values:
        for distance in distance_values:
            combination_count += 1
            
            print(f"\n📈 진행률: {combination_count}/{total_combinations} "
                  f"({combination_count/total_combinations*100:.1f}%)")
            print(f"🎯 현재 테스트: height={height:.3f}, distance={int(distance)}")
            
            try:
                start_time = time.time()
                
                # 현재 파라미터로 결과 계산
                ptk_result = pd.DataFrame(columns=['peo_2nd', 'teo_2nd', 'keo_2nd', 'ptk_2nd'])
                
                for wav_file in wav_files:
                    parts = wav_file.replace(folder, '').strip(os.sep).split(os.sep)
                    if len(parts) > 0:
                        index_key = parts[0]
                    else:
                        index_key = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(wav_file))))
                    
                    if index_key not in ptk_result.index:
                        ptk_result.loc[index_key] = [None, None, None, None]
                    
                    filename = os.path.basename(wav_file)
                    
                    # 직접 로드 방식으로 피크 카운트
                    if 'p_2_' in filename:
                        result = count_peaks_direct_load(wav_file, height=height, distance=distance)
                        ptk_result.loc[index_key, 'peo_2nd'] = result
                    elif 'p_5_' in filename:
                        result = count_peaks_direct_load(wav_file, height=height, distance=distance)
                        ptk_result.loc[index_key, 'teo_2nd'] = result
                    elif 'p_8_' in filename:
                        result = count_peaks_direct_load(wav_file, height=height, distance=distance)
                        ptk_result.loc[index_key, 'keo_2nd'] = result
                    elif 'p_11_' in filename:
                        result = count_peaks_direct_load(wav_file, height=height, distance=distance)
                        ptk_result.loc[index_key, 'ptk_2nd'] = round(result/3, 1)
                
                # 상관계수 계산
                ptk_result.index = ptk_result.index.astype(int)
                correlation_results = {}
                
                for col in ptk_result.columns:
                    if col in ptk_label.columns:
                        temp_combined = pd.concat([ptk_result[col], ptk_label[col]], axis=1, join="inner").dropna()
                        if not temp_combined.empty:
                            correlation = temp_combined.corr(method='pearson').iloc[0, 1]
                            correlation_results[col] = correlation if not pd.isna(correlation) else 0
                        else:
                            correlation_results[col] = 0
                
                if not correlation_results:
                    continue
                
                avg_correlation = np.mean(list(correlation_results.values()))
                max_correlation = max(correlation_results.values())
                
                elapsed_time = time.time() - start_time
                
                result_entry = {
                    'height': height,
                    'distance': distance,
                    'avg_correlation': avg_correlation,
                    'max_correlation': max_correlation,
                    'elapsed_time': elapsed_time
                }
                
                for col, corr in correlation_results.items():
                    result_entry[f'{col}_correlation'] = corr
                
                optimization_results.append(result_entry)
                
                print(f"✅ 평균: {avg_correlation:.4f}, 최대: {max_correlation:.4f}")
                
            except Exception as e:
                print(f"❌ 오류: {e}")
                continue
    
    # 결과 처리
    results_df = pd.DataFrame(optimization_results)
    if results_df.empty:
        return None, None
    
    results_df.to_csv('H:/ptk_optimization_direct.csv', index=False)
    
    best_avg = results_df.loc[results_df['avg_correlation'].idxmax()]
    best_max = results_df.loc[results_df['max_correlation'].idxmax()]
    
    print("\n🏆 최적화 결과 (직접 로드):")
    print("="*60)
    print(f"최고 평균 상관계수: {best_avg['avg_correlation']:.6f}")
    print(f"최적 height: {best_avg['height']:.3f}")
    print(f"최적 distance: {int(best_avg['distance'])}")
    
    for col in ['peo_2nd', 'teo_2nd', 'keo_2nd', 'ptk_2nd']:
        if f'{col}_correlation' in best_avg:
            print(f"  {col}: {best_avg[f'{col}_correlation']:.4f}")
    print("="*60)
    
    return results_df, best_avg, best_max

if __name__ == "__main__":
    result = optimize_ptk_direct()
    if result[0] is not None:
        print("💾 직접 로드 방식 결과 저장 완료!")
    else:
        print("❌ 직접 로드 방식 실패")