import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import warnings
import hashlib
import pickle
warnings.filterwarnings('ignore')

# 필요한 라이브러리들
import librosa
import scipy.signal
from pydub import AudioSegment

class AudioCache:
    """오디오 전처리 결과를 캐싱하는 클래스"""
    
    def __init__(self, cache_dir='H:/audio_cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        print(f"📁 캐시 디렉토리: {cache_dir}")
    
    def get_cache_key(self, filepath):
        """파일 경로를 기반으로 캐시 키 생성"""
        file_stat = os.stat(filepath)
        key_string = f"{filepath}_{file_stat.st_size}_{file_stat.st_mtime}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_cached_audio(self, filepath):
        """캐시에서 전처리된 오디오 데이터 가져오기"""
        cache_key = self.get_cache_key(filepath)
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        return None
    
    def save_cached_audio(self, filepath, audio_data):
        """전처리된 오디오 데이터를 캐시에 저장"""
        cache_key = self.get_cache_key(filepath)
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(audio_data, f)
        except Exception as e:
            print(f"⚠️ 캐시 저장 실패: {e}")

def convert_audio_for_model_cached(filepath, cache, EXPECTED_SAMPLE_RATE=16000):
    """캐싱을 사용한 오디오 변환"""
    # 캐시 확인
    cached_data = cache.get_cached_audio(filepath)
    if cached_data is not None:
        return cached_data
    
    # 캐시가 없으면 새로 변환
    try:
        audio = AudioSegment.from_file(filepath)
        audio = audio.set_frame_rate(EXPECTED_SAMPLE_RATE).set_channels(1)
        
        # 임시 파일 없이 바이트 데이터로 처리
        audio_bytes = audio.export(format="wav").read()
        
        # librosa로 바이트 데이터 로드
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=EXPECTED_SAMPLE_RATE)
        
        # 3초 자르고 정규화
        y_trimmed = y[:sr * 3]
        if np.max(np.abs(y_trimmed)) > 0:
            y_trimmed = y_trimmed / np.max(np.abs(y_trimmed))
        
        audio_data = {
            'audio': y_trimmed,
            'sr': sr
        }
        
        # 캐시에 저장
        cache.save_cached_audio(filepath, audio_data)
        
        return audio_data
        
    except Exception as e:
        print(f"⚠️ 오디오 변환 실패 {filepath}: {e}")
        return None

def count_peaks_cached(filepath, cache, height=0.05, distance=3000, plot=False):
    """캐싱을 사용한 피크 카운팅"""
    try:
        audio_data = convert_audio_for_model_cached(filepath, cache)
        if audio_data is None:
            return 0
        
        y_trimmed = audio_data['audio']
        
        if len(y_trimmed) == 0:
            return 0
        
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
        print(f"⚠️ 피크 카운팅 오류 {filepath}: {e}")
        return 0

def optimize_ptk_cached():
    """캐싱을 사용한 PTK 파라미터 최적화"""
    print("🔍 PTK 파라미터 최적화 (캐싱 사용)...")
    
    # 캐시 초기화
    cache = AudioCache()
    
    # 파라미터 범위
    height_values = np.arange(0.03, 0.08, 0.005)
    distance_values = np.arange(2500, 3500, 100)
    
    print(f"📊 테스트할 조합 수: {len(height_values) * len(distance_values)}")
    
    # 데이터 로드
    folder = r'C:\Users\user\Downloads\data'
    pattern = os.path.join(folder, '**', 'CLAP_D', '1', 'p*.wav')
    wav_files = glob.glob(pattern, recursive=True)
    print(f"🎵 발견된 WAV 파일 수: {len(wav_files)}")
    
    # 라벨 데이터 로드
    df = pd.read_csv(r'H:\labeled_data_D.csv', header=1, index_col=0)
    ptk_label = df.loc[:, ['peo_2nd', 'teo_2nd', 'keo_2nd', 'ptk_2nd']]
    
    # 1단계: 모든 파일을 미리 캐싱
    print("📦 오디오 파일 사전 캐싱 중...")
    for i, wav_file in enumerate(wav_files):
        print(f"캐싱: {i+1}/{len(wav_files)} - {os.path.basename(wav_file)}", end='\r')
        convert_audio_for_model_cached(wav_file, cache)
    print("\n✅ 사전 캐싱 완료!")
    
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
                    
                    # 캐싱된 데이터로 피크 카운트
                    if 'p_2_' in filename:
                        result = count_peaks_cached(wav_file, cache, height=height, distance=distance)
                        ptk_result.loc[index_key, 'peo_2nd'] = result
                    elif 'p_5_' in filename:
                        result = count_peaks_cached(wav_file, cache, height=height, distance=distance)
                        ptk_result.loc[index_key, 'teo_2nd'] = result
                    elif 'p_8_' in filename:
                        result = count_peaks_cached(wav_file, cache, height=height, distance=distance)
                        ptk_result.loc[index_key, 'keo_2nd'] = result
                    elif 'p_11_' in filename:
                        result = count_peaks_cached(wav_file, cache, height=height, distance=distance)
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
                
                print(f"✅ 평균: {avg_correlation:.4f}, 최대: {max_correlation:.4f}, 시간: {elapsed_time:.2f}초")
                
            except Exception as e:
                print(f"❌ 오류: {e}")
                continue
    
    # 결과 처리
    results_df = pd.DataFrame(optimization_results)
    if results_df.empty:
        return None, None
    
    results_df.to_csv('H:/ptk_optimization_cached.csv', index=False)
    
    best_avg = results_df.loc[results_df['avg_correlation'].idxmax()]
    best_max = results_df.loc[results_df['max_correlation'].idxmax()]
    
    print("\n🏆 최적화 결과 (캐싱 사용):")
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
    import io  # BytesIO 사용을 위해 추가
    
    result = optimize_ptk_cached()
    if result[0] is not None:
        print("💾 캐싱 방식 결과 저장 완료!")
    else:
        print("❌ 캐싱 방식 실패")