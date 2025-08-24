import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import product
import time
import warnings
warnings.filterwarnings('ignore')

# ptk_sound.py의 함수들을 임포트
import sys
sys.path.append('H:/')

# 필요한 라이브러리들
import librosa
import scipy.signal
from pydub import AudioSegment

def convert_audio_for_model(user_file, output_file=None, EXPECTED_SAMPLE_RATE=16000):
    """오디오 파일을 모델에 맞게 변환 (모노채널 + 정규화)"""
    import tempfile
    import uuid
    
    if output_file is None:
        # 고유한 임시 파일명 생성
        output_file = os.path.join(tempfile.gettempdir(), f"converted_audio_{uuid.uuid4().hex}.wav")
    
    audio = AudioSegment.from_file(user_file)
    audio = audio.set_frame_rate(EXPECTED_SAMPLE_RATE).set_channels(1)
    audio.export(output_file, format="wav")
    return output_file

def count_peaks_from_waveform_optimized(filepath, height=0.05, distance=3000, plot=False):
    """
    최적화된 피크 카운팅 함수 (ptk_sound.py에서 가져옴)
    """
    temp_file = None
    try:
        temp_file = convert_audio_for_model(filepath)
        y, sr = librosa.load(temp_file, sr=None)
        # 3초 자르기
        y_trimmed = y[:sr * 3]
        
        if np.max(np.abs(y_trimmed)) == 0:
            return 0
            
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
    finally:
        # 임시 파일 정리
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass

def optimize_ptk_parameters():
    """
    PTK 파라미터 최적화 파이프라인
    """
    print("🔍 PTK 파라미터 최적화 파이프라인 시작...")
    
    # 최적화할 파라미터 범위 설정 (원본 파라미터 주변에서 세밀하게)
    height_values = np.arange(0.02, 0.12, 0.005)  # 0.02 ~ 0.115, 0.005 간격 (원본 0.05 주변)
    distance_values = np.arange(2000, 5000, 200)  # 2000 ~ 4800, 200 간격 (원본 3000 주변)
    
    print(f"📊 테스트할 조합 수: {len(height_values) * len(distance_values)}")
    
    # 데이터 로드
    folder = r'C:\Users\user\Downloads\data'
    pattern = os.path.join(folder, '**', 'CLAP_D', '1', 'p*.wav')
    wav_files = glob.glob(pattern, recursive=True)
    print(f"🎵 발견된 WAV 파일 수: {len(wav_files)}")
    
    # 라벨 데이터 로드
    df = pd.read_csv(r'H:\labeled_data_D.csv', header=1, index_col=0)
    ptk_label = df.loc[:, ['peo_2nd', 'teo_2nd', 'keo_2nd', 'ptk_2nd']]
    
    # 최적화 결과를 저장할 리스트
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
                    # Windows 경로 처리를 위해 replace를 수정
                    parts = wav_file.replace(folder, '').strip(os.sep).split(os.sep)
                    if len(parts) > 0:
                        index_key = parts[0]
                    else:
                        index_key = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(wav_file))))
                    
                    if index_key not in ptk_result.index:
                        ptk_result.loc[index_key] = [None, None, None, None]
                    
                    filename = os.path.basename(wav_file)
                    
                    # 각 음성 유형별로 피크 카운트
                    if 'p_2_' in filename:  # peo_2nd
                        result = count_peaks_from_waveform_optimized(wav_file, height=height, distance=distance)
                        ptk_result.loc[index_key, 'peo_2nd'] = result
                    elif 'p_5_' in filename:  # teo_2nd
                        result = count_peaks_from_waveform_optimized(wav_file, height=height, distance=distance)
                        ptk_result.loc[index_key, 'teo_2nd'] = result
                    elif 'p_7_' in filename:  # keo_2nd
                        result = count_peaks_from_waveform_optimized(wav_file, height=height, distance=distance)
                        ptk_result.loc[index_key, 'keo_2nd'] = result
                    elif 'p_10_' in filename:  # ptk_2nd
                        result = count_peaks_from_waveform_optimized(wav_file, height=height, distance=distance)
                        ptk_result.loc[index_key, 'ptk_2nd'] = round(result/3, 1)
                
                # 결과가 있는지 확인
                if ptk_result.dropna(how='all').empty:
                    print("❌ 분석 결과가 없습니다.")
                    continue
                
                # 상관계수 계산 - 각 열별로
                ptk_result.index = ptk_result.index.astype(int)
                correlation_results = {}
                
                for col in ptk_result.columns:
                    if col in ptk_label.columns:
                        # 인덱스를 맞춘 후 NaN 값 제거하여 상관계수 계산
                        combined = pd.concat([ptk_result[col], ptk_label[col]], axis=1, join="inner").dropna()
                        
                        if not combined.empty and len(combined) > 1:
                            correlation = combined.corr(method='pearson').iloc[0, 1]
                            if not pd.isna(correlation):
                                correlation_results[col] = correlation
                            else:
                                correlation_results[col] = 0
                        else:
                            correlation_results[col] = 0
                
                if not correlation_results:
                    print("❌ 상관계수 계산 실패")
                    continue
                
                # 평균 상관계수 계산
                avg_correlation = np.mean(list(correlation_results.values()))
                max_correlation = max(correlation_results.values())
                
                elapsed_time = time.time() - start_time
                
                # 결과 저장
                result_entry = {
                    'height': height,
                    'distance': distance,
                    'avg_correlation': avg_correlation,
                    'max_correlation': max_correlation,
                    'elapsed_time': elapsed_time,
                    'valid_samples': len(ptk_result.dropna(how='all'))
                }
                
                # 각 열별 상관계수도 저장
                for col, corr in correlation_results.items():
                    result_entry[f'{col}_correlation'] = corr
                
                optimization_results.append(result_entry)
                
                print(f"✅ 평균 상관계수: {avg_correlation:.4f}, 최대: {max_correlation:.4f}, 처리시간: {elapsed_time:.2f}초")
                
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
                continue
    
    # 결과를 DataFrame으로 변환
    results_df = pd.DataFrame(optimization_results)
    
    if results_df.empty:
        print("❌ 최적화 결과가 없습니다.")
        return None, None
    
    # 결과 저장
    results_df.to_csv('H:/ptk_optimization_results.csv', index=False)
    print(f"💾 결과 저장 완료: H:/ptk_optimization_results.csv")
    
    # 평균 상관계수 기준 최고 결과
    best_avg = results_df.loc[results_df['avg_correlation'].idxmax()]
    
    # 최대 상관계수 기준 최고 결과
    best_max = results_df.loc[results_df['max_correlation'].idxmax()]
    
    print("\n🏆 최적화 결과 (평균 상관계수 기준):")
    print("="*60)
    print(f"최고 평균 상관계수: {best_avg['avg_correlation']:.6f}")
    print(f"최적 height: {best_avg['height']:.3f}")
    print(f"최적 distance: {int(best_avg['distance'])}")
    print(f"유효 샘플 수: {int(best_avg['valid_samples'])}")
    print(f"처리 시간: {best_avg['elapsed_time']:.2f}초")
    
    print("\n🎯 개별 열 상관계수:")
    for col in ['peo_2nd', 'teo_2nd', 'keo_2nd', 'ptk_2nd']:
        if f'{col}_correlation' in best_avg:
            print(f"  {col}: {best_avg[f'{col}_correlation']:.4f}")
    print("="*60)
    
    print("\n🏆 최적화 결과 (최대 상관계수 기준):")
    print("="*60)
    print(f"최고 최대 상관계수: {best_max['max_correlation']:.6f}")
    print(f"최적 height: {best_max['height']:.3f}")
    print(f"최적 distance: {int(best_max['distance'])}")
    print("="*60)
    
    return results_df, best_avg, best_max

def visualize_ptk_optimization_results(results_df):
    """
    PTK 최적화 결과를 시각화
    """
    print("📊 결과 시각화 중...")
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    
    # 1. 평균 상관계수 히스토그램
    axes[0, 0].hist(results_df['avg_correlation'], bins=30, alpha=0.7, color='lightblue', edgecolor='black')
    axes[0, 0].set_xlabel('Average Correlation Coefficient')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('Distribution of Average Correlation Coefficients')
    axes[0, 0].axvline(results_df['avg_correlation'].max(), color='red', linestyle='--', 
                       label=f'Max: {results_df["avg_correlation"].max():.4f}')
    axes[0, 0].legend()
    
    # 2. Height vs 평균 상관계수
    scatter1 = axes[0, 1].scatter(results_df['height'], results_df['avg_correlation'], 
                                 c=results_df['distance'], cmap='viridis', alpha=0.6)
    axes[0, 1].set_xlabel('Height Threshold')
    axes[0, 1].set_ylabel('Average Correlation Coefficient')
    axes[0, 1].set_title('Height vs Average Correlation (colored by Distance)')
    plt.colorbar(scatter1, ax=axes[0, 1], label='Distance')
    
    # 3. Distance vs 평균 상관계수
    scatter2 = axes[0, 2].scatter(results_df['distance'], results_df['avg_correlation'], 
                                 c=results_df['height'], cmap='plasma', alpha=0.6)
    axes[0, 2].set_xlabel('Distance Threshold')
    axes[0, 2].set_ylabel('Average Correlation Coefficient')
    axes[0, 2].set_title('Distance vs Average Correlation (colored by Height)')
    plt.colorbar(scatter2, ax=axes[0, 2], label='Height')
    
    # 4. 히트맵 - Height vs Distance
    pivot_table = results_df.pivot_table(values='avg_correlation', index='height', columns='distance', aggfunc='mean')
    im = axes[1, 0].imshow(pivot_table.values, aspect='auto', cmap='RdYlBu_r', origin='lower')
    axes[1, 0].set_xlabel('Distance Index')
    axes[1, 0].set_ylabel('Height Index')
    axes[1, 0].set_title('Average Correlation Heatmap')
    plt.colorbar(im, ax=axes[1, 0])
    
    # 5. Top 10 결과
    top_10 = results_df.nlargest(10, 'avg_correlation')
    axes[1, 1].barh(range(len(top_10)), top_10['avg_correlation'])
    axes[1, 1].set_yticks(range(len(top_10)))
    axes[1, 1].set_yticklabels([f"h:{row['height']:.3f}, d:{int(row['distance'])}" 
                               for _, row in top_10.iterrows()])
    axes[1, 1].set_xlabel('Average Correlation Coefficient')
    axes[1, 1].set_title('Top 10 Parameter Combinations')
    
    # 6. 개별 열 상관계수 비교 (상위 5개)
    top_5 = results_df.nlargest(5, 'avg_correlation')
    cols = ['peo_2nd_correlation', 'teo_2nd_correlation', 'keo_2nd_correlation', 'ptk_2nd_correlation']
    
    for i, (_, row) in enumerate(top_5.iterrows()):
        values = [row.get(col, 0) for col in cols]
        axes[1, 2].bar([j + i*0.15 for j in range(len(cols))], values, 
                      width=0.15, label=f"h:{row['height']:.3f}, d:{int(row['distance'])}", alpha=0.7)
    
    axes[1, 2].set_xlabel('PTK Columns')
    axes[1, 2].set_ylabel('Correlation Coefficient')
    axes[1, 2].set_title('Individual Column Correlations (Top 5)')
    axes[1, 2].set_xticks(range(len(cols)))
    axes[1, 2].set_xticklabels(['peo_2nd', 'teo_2nd', 'keo_2nd', 'ptk_2nd'])
    axes[1, 2].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig('H:/ptk_optimization_visualization.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 3D 시각화
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    scatter = ax.scatter(results_df['height'], 
                        results_df['distance'], 
                        results_df['avg_correlation'],
                        c=results_df['max_correlation'], 
                        cmap='coolwarm', 
                        s=50, 
                        alpha=0.6)
    
    ax.set_xlabel('Height Threshold')
    ax.set_ylabel('Distance Threshold')
    ax.set_zlabel('Average Correlation Coefficient')
    ax.set_title('3D PTK Parameter Optimization Results')
    plt.colorbar(scatter, label='Max Correlation')
    
    plt.savefig('H:/ptk_optimization_3d.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("💾 시각화 결과 저장 완료:")
    print("  - H:/ptk_optimization_visualization.png")
    print("  - H:/ptk_optimization_3d.png")

def analyze_ptk_parameter_sensitivity(results_df):
    """
    PTK 파라미터의 민감도 분석
    """
    print("🔬 PTK 파라미터 민감도 분석...")
    
    # 각 파라미터별 평균 상관계수
    height_sensitivity = results_df.groupby('height')['avg_correlation'].agg(['mean', 'std', 'count'])
    distance_sensitivity = results_df.groupby('distance')['avg_correlation'].agg(['mean', 'std', 'count'])
    
    # 결과 출력
    print("\n📈 Height Threshold 민감도:")
    print(f"최고 평균 상관계수: {height_sensitivity['mean'].max():.4f} (height: {height_sensitivity['mean'].idxmax():.3f})")
    
    print("\n📈 Distance Threshold 민감도:")
    print(f"최고 평균 상관계수: {distance_sensitivity['mean'].max():.4f} (distance: {int(distance_sensitivity['mean'].idxmax())})")
    
    # 민감도 시각화
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # Height Threshold
    axes[0].errorbar(height_sensitivity.index, height_sensitivity['mean'], 
                     yerr=height_sensitivity['std'], capsize=3, marker='o')
    axes[0].set_xlabel('Height Threshold')
    axes[0].set_ylabel('Mean Average Correlation')
    axes[0].set_title('Height Threshold Sensitivity')
    axes[0].grid(True, alpha=0.3)
    
    # Distance Threshold
    axes[1].errorbar(distance_sensitivity.index, distance_sensitivity['mean'], 
                     yerr=distance_sensitivity['std'], capsize=3, marker='s')
    axes[1].set_xlabel('Distance Threshold')
    axes[1].set_ylabel('Mean Average Correlation')
    axes[1].set_title('Distance Threshold Sensitivity')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('H:/ptk_parameter_sensitivity_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return height_sensitivity, distance_sensitivity

if __name__ == "__main__":
    # 최적화 실행
    result = optimize_ptk_parameters()
    
    if result[0] is not None:
        results_df, best_avg, best_max = result
        
        # 결과 시각화
        visualize_ptk_optimization_results(results_df)
        
        # 민감도 분석
        height_sens, distance_sens = analyze_ptk_parameter_sensitivity(results_df)
        
        # 최종 보고서 저장
        with open('H:/ptk_optimization_report.txt', 'w', encoding='utf-8') as f:
            f.write("🏆 PTK 파라미터 최적화 보고서\n")
            f.write("="*60 + "\n\n")
            
            f.write("📊 평균 상관계수 기준 최적 결과:\n")
            f.write(f"최고 평균 상관계수: {best_avg['avg_correlation']:.6f}\n")
            f.write(f"최적 height: {best_avg['height']:.3f}\n")
            f.write(f"최적 distance: {int(best_avg['distance'])}\n")
            f.write(f"유효 샘플 수: {int(best_avg['valid_samples'])}\n")
            f.write(f"처리 시간: {best_avg['elapsed_time']:.2f}초\n\n")
            
            f.write("🎯 개별 열별 상관계수 (평균 기준):\n")
            for col in ['peo_2nd', 'teo_2nd', 'keo_2nd', 'ptk_2nd']:
                if f'{col}_correlation' in best_avg:
                    f.write(f"  {col}: {best_avg[f'{col}_correlation']:.4f}\n")
            f.write("\n")
            
            f.write("📊 최대 상관계수 기준 최적 결과:\n")
            f.write(f"최고 최대 상관계수: {best_max['max_correlation']:.6f}\n")
            f.write(f"최적 height: {best_max['height']:.3f}\n")
            f.write(f"최적 distance: {int(best_max['distance'])}\n\n")
            
            f.write("📊 상위 10개 결과 (평균 상관계수 기준):\n")
            f.write("-"*40 + "\n")
            top_10 = results_df.nlargest(10, 'avg_correlation')
            for idx, (_, row) in enumerate(top_10.iterrows(), 1):
                f.write(f"{idx:2d}. 평균 상관계수: {row['avg_correlation']:.4f} | "
                       f"height: {row['height']:.3f} | "
                       f"distance: {int(row['distance'])}\n")
        
        print("\n💾 최종 보고서 저장 완료: H:/ptk_optimization_report.txt")
        print("🎉 PTK 최적화 파이프라인 완료!")
    else:
        print("❌ PTK 최적화 실패: 유효한 결과가 없습니다.")