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
sys.path.append('/Volumes/SSAM/aptk_model')

# 필요한 라이브러리들
import librosa
import scipy.signal
from pydub import AudioSegment

def convert_audio_for_model(user_file, output_file=None, EXPECTED_SAMPLE_RATE=16000):
    """오디오 파일을 모델에 맞게 변환 (모노채널 + 정규화)"""
    import tempfile
    import uuid
    
    # 임시 파일을 자동으로 삭제되도록 NamedTemporaryFile 사용
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_file.close()
    
    try:
        audio = AudioSegment.from_file(user_file)
        audio = audio.set_frame_rate(EXPECTED_SAMPLE_RATE).set_channels(1)
        audio.export(temp_file.name, format="wav")
        return temp_file.name
    except Exception as e:
        # 오류 발생 시 임시 파일 정리
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise e

# def count_peaks_from_waveform_optimized(filepath, n=3, height=0.36, distance=2500, plot=False):
#     """
#     최적화된 피크 카운팅 함수 (임시 파일 즉시 정리 포함)
#     """
#     converted_file = None
#     try:
#         # 한 번만 변환하고 즉시 사용
#         converted_file = convert_audio_for_model(filepath)
#         y, sr = librosa.load(converted_file, sr=None)
        
#         # 임시 파일을 즉시 삭제 (메모리에 이미 로드됨)
#         if converted_file and os.path.exists(converted_file):
#             try:
#                 os.unlink(converted_file)
#                 converted_file = None  # 삭제되었음을 표시
#             except:
#                 pass
        
#         # n초 자르기
#         y_trimmed = y[:sr * int(n)]
        
#         if np.max(np.abs(y_trimmed)) == 0:
#             return 0
            
#         y_trimmed = y_trimmed / np.max(np.abs(y_trimmed))
        
#         # 피크 탐지
#         peaks, _ = scipy.signal.find_peaks(y_trimmed, height=height, distance=distance)
        
#         if plot:
#             plt.figure(figsize=(12, 4))
#             plt.plot(y_trimmed)
#             plt.plot(peaks, y_trimmed[peaks], "rx")
#             plt.title(f"Detected Peaks: {len(peaks)}")
#             plt.show()
            
#         # peak가 2개 이상일 때만 시간 기반 계산 가능
#         if len(peaks) >= 2:
#             # 첫 번째 peak와 마지막 peak 사이의 시간 계산 (초 단위)
#             first_peak_time = peaks[0] / sr
#             last_peak_time = peaks[-1] / sr
#             time_length = last_peak_time - first_peak_time
            
#             # 시간이 0보다 클 때만 나누기
#             if time_length > 0:
#                 return len(peaks) / time_length  # 평균 peak rate (peaks per second)
#             else:
#                 return len(peaks)  # 시간 차이가 0이면 단순 개수 반환
#         elif len(peaks) == 1:
#             return 0  # peak가 1개면 rate 계산 불가능하므로 0
#         else:
#             return None  # peak가 없으면 null
            
#     except Exception as e:
#         print(f"⚠️ 파일 처리 오류 {filepath}: {e}")
#         return 0
#     finally:
#         # 혹시 남아있는 임시 파일 정리
#         if converted_file and os.path.exists(converted_file):
#             try:
#                 os.unlink(converted_file)
#             except:
#                 pass

def count_peaks_from_waveform_wholetime(filepath, n=10, height=0.14, distance=2400, plot=False):
    """
    파일 전체 시간을 기준으로 peak rate를 계산하는 함수
    """
    converted_file = None
    try:
        # 한 번만 변환하고 즉시 사용
        converted_file = convert_audio_for_model(filepath)
        y, sr = librosa.load(converted_file, sr=None)
        
        # 임시 파일을 즉시 삭제 (메모리에 이미 로드됨)
        if converted_file and os.path.exists(converted_file):
            try:
                os.unlink(converted_file)
                converted_file = None  # 삭제되었음을 표시
            except:
                pass

        # n초 자르기
        y_trimmed = y[:sr * int(n)]
        
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
        
        # y_trimmed의 총 시간 계산
        y_trimmed_total_time = len(y_trimmed) / sr
        
        if len(peaks) > 0 and y_trimmed_total_time > 0:
            return len(peaks) / y_trimmed_total_time  # y_trimmed 시간 대비 peak rate (초당 peak 개수)
        elif len(peaks) == 0:
            return None  # peak가 없으면 null
        else:
            return 0  # 시간이 0이면 0
            
    except Exception as e:
        print(f"⚠️ 파일 처리 오류 {filepath}: {e}")
        return 0
    finally:
        # 임시 파일 정리
        if converted_file and os.path.exists(converted_file):
            try:
                os.unlink(converted_file)
            except:
                pass

def optimize_ptk_parameters():
    """
    PTK 파라미터 최적화 파이프라인
    """
    print("🔍 PTK 파라미터 최적화 파이프라인 시작...")
    
    # 최적화할 파라미터 범위 설정 (원본 파라미터 주변에서 세밀하게)
    # height_values = np.arange(0.1, 0.5, 0.01)  # 0.02 ~ 0.115, 0.005 간격 (원본 0.05 주변)
    height_values=np.arange(.1,.25,.01)
    distance_values = np.arange(2400, 3000, 100)  # 2000 ~ 4800, 200 간격 (원본 3000 주변)
    n_values=np.arange(8,12,1)
    
    print(f"📊 테스트할 조합 수: {len(height_values) * len(distance_values)*len(n_values)}")
    
    # 데이터 로드
    folder = '/Volumes/SSAM/project/files/upload'
    pattern = os.path.join(folder, '**', 'CLAP_D', '1', 'p*.wav')
    wav_files = glob.glob(pattern, recursive=True)
    print(f"🎵 발견된 WAV 파일 수: {len(wav_files)}")
    
    # 라벨 데이터 로드
    df = pd.read_csv('/Volumes/SSAM/aptk_model/labeled_data_D.csv', header=1, index_col=0)
    ptk_label = df.loc[:, ['peo_3rd', 'keo_3rd']]
    
    # 최적화 결과를 저장할 리스트
    optimization_results = []
    
    total_combinations = len(height_values) * len(distance_values)*len(n_values)
    combination_count = 0
    
    print("🚀 최적화 시작...")
    
    for height in height_values:
     for n in n_values:
        for distance in distance_values:
            combination_count += 1
            
            print(f"\n📈 진행률: {combination_count}/{total_combinations} "
                  f"({combination_count/total_combinations*100:.1f}%)")
            print(f"🎯 현재 테스트: height={height:.3f}, distance={int(distance)},n={n}")
            
            try:
                start_time = time.time()
                
                # 현재 파라미터로 결과 계산
                ptk_result = pd.DataFrame(columns=['peo_3rd', 'keo_3rd'])
                
                for wav_file in wav_files:
                    # Windows 경로 처리를 위해 replace를 수정
                    parts = wav_file.replace(folder, '').strip(os.sep).split(os.sep)
                    if len(parts) > 0:
                        index_key = parts[0]
                    else:
                        index_key = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(wav_file))))
                    
                    if index_key not in ptk_result.index:
                        ptk_result.loc[index_key] = [None, None]
                    
                    filename = os.path.basename(wav_file)
                    
                    # 각 음성 유형별로 피크 카운트
                    if 'p_3_' in filename:  # peo_3rd
                        result = count_peaks_from_waveform_wholetime(wav_file, n=n,height=height, distance=distance)
                        ptk_result.loc[index_key, 'peo_3rd'] = result
                    # elif 'p_6_' in filename:  # teo_3rd
                    #     result = count_peaks_from_waveform_optimized(wav_file,n=n, height=height, distance=distance)
                    #     ptk_result.loc[index_key, 'teo_3rd'] = result
                    elif 'p_9_' in filename:  # keo_3rd
                        result = count_peaks_from_waveform_wholetime(wav_file, n=n,height=height, distance=distance)
                        ptk_result.loc[index_key, 'keo_3rd'] = result
                    # elif 'p_12_' in filename:  # ptk_3rd
                    #     result = count_peaks_from_waveform_optimized(wav_file, n=n,height=height, distance=distance)
                    #     ptk_result.loc[index_key, 'ptk_3rd'] = result
                
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
                    'n':n,
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
    results_df.to_csv('/Volumes/SSAM/aptk_model/ptk_3rd_optimization_results.csv', index=False)
    print(f"💾 결과 저장 완료: /Volumes/SSAM/aptk_model/ptk_3rd_optimization_results.csv")
    
    # 평균 상관계수 기준 최고 결과
    best_avg = results_df.loc[results_df['avg_correlation'].idxmax()]
    
    # 최대 상관계수 기준 최고 결과
    best_max = results_df.loc[results_df['max_correlation'].idxmax()]
    
    print("\n🏆 최적화 결과 (평균 상관계수 기준):")
    print("="*60)
    print(f"최고 평균 상관계수: {best_avg['avg_correlation']:.6f}")
    print(f"최적 height: {best_avg['height']:.3f}")
    print(f"최적 distance: {int(best_avg['distance'])}")
    print(f"최적 n: {best_avg['n']}")
    print(f"유효 샘플 수: {int(best_avg['valid_samples'])}")
    print(f"처리 시간: {best_avg['elapsed_time']:.2f}초")
    
    print("\n🎯 개별 열 상관계수:")
    for col in ['peo_3rd', 'keo_3rd']:
        if f'{col}_correlation' in best_avg:
            print(f"  {col}: {best_avg[f'{col}_correlation']:.4f}")
    print("="*60)
    
    print("\n🏆 최적화 결과 (최대 상관계수 기준):")
    print("="*60)
    print(f"최고 최대 상관계수: {best_max['max_correlation']:.6f}")
    print(f"최적 height: {best_max['height']:.3f}")
    print(f"최적 distance: {int(best_max['distance'])}")
    print(f"최적 n: {int(best_max['n'])}")

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
    cols = ['peo_3rd_correlation', 'keo_3rd_correlation']
    
    for i, (_, row) in enumerate(top_5.iterrows()):
        values = [row.get(col, 0) for col in cols]
        axes[1, 2].bar([j + i*0.15 for j in range(len(cols))], values, 
                      width=0.15, label=f"h:{row['height']:.3f}, d:{int(row['distance'])}", alpha=0.7)
    
    axes[1, 2].set_xlabel('PTK Columns')
    axes[1, 2].set_ylabel('Correlation Coefficient')
    axes[1, 2].set_title('Individual Column Correlations (Top 5)')
    axes[1, 2].set_xticks(range(len(cols)))
    axes[1, 2].set_xticklabels(['peo_3rd', 'keo_3rd'])
    axes[1, 2].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig('/Volumes/SSAM/aptk_model/ptk_3rd_optimization_visualization.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("💾 시각화 결과 저장 완료:")
    print("  - /Volumes/SSAM/aptk_model/ptk_3rd_optimization_visualization.png")

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
    plt.savefig('/Volumes/SSAM/aptk_model/ptk_3rd_parameter_sensitivity_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return height_sensitivity, distance_sensitivity

def create_excel_comparison(results_df, best_params):
    """
    최적 파라미터로 계산된 결과와 실제 라벨을 Excel로 비교
    """
    print("📊 Excel 비교 파일 생성 중...")
    
    # 데이터 로드
    folder = '/Volumes/SSAM/project/files/upload'
    pattern = os.path.join(folder, '**', 'CLAP_D', '1', 'p*.wav')
    wav_files = glob.glob(pattern, recursive=True)
    
    df = pd.read_csv('/Volumes/SSAM/aptk_model/labeled_data_D.csv', header=1, index_col=0)
    ptk_label = df.loc[:, ['peo_3rd', 'keo_3rd']]
    
    # 최적 파라미터로 결과 재계산
    best_height = best_params['height']
    best_distance = best_params['distance']
    
    ptk_result = pd.DataFrame(columns=['peo_3rd', 'keo_3rd'])
    
    for wav_file in wav_files:
        parts = wav_file.replace(folder, '').strip(os.sep).split(os.sep)
        if len(parts) > 0:
            index_key = parts[0]
        else:
            index_key = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(wav_file))))
        
        if index_key not in ptk_result.index:
            ptk_result.loc[index_key] = [None, None]
        
        filename = os.path.basename(wav_file)
        
        if 'p_3_' in filename:
            result = count_peaks_from_waveform_wholetime(wav_file, n=best_params.get('n', 3), height=best_height, distance=best_distance)
            ptk_result.loc[index_key, 'peo_3rd'] = result
        # elif 'p_6_' in filename:
        #     result = count_peaks_from_waveform_optimized(wav_file, height=best_height, distance=best_distance)
        #     ptk_result.loc[index_key, 'teo_3rd'] = result
        elif 'p_9_' in filename:
            result = count_peaks_from_waveform_wholetime(wav_file, n=best_params.get('n', 3), height=best_height, distance=best_distance)
            ptk_result.loc[index_key, 'keo_3rd'] = result
        # elif 'p_12_' in filename:
        #     result = count_peaks_from_waveform_optimized(wav_file, n=best_params.get('n', 3), height=best_height, distance=best_distance)
        #     ptk_result.loc[index_key, 'ptk_3rd'] = result
    
    # 결과를 저장할 리스트
    comparison_data = []
    
    # 공통 환자 ID 찾기
    ptk_result.index = ptk_result.index.astype(int)
    common_ids = set(df.index) & set(ptk_label.index) & set(ptk_result.index)
    
    for patient_id in sorted(common_ids):
        try:
            patient_number = df.loc[patient_id, 'number']
            
            # 예측 총점 계산 (실제 라벨의 합)
            predicted_total = ptk_label.loc[patient_id].sum()
            
            # 실제 총점 계산 (최적화된 결과의 합)
            actual_total = ptk_result.loc[patient_id].sum()
            
            # NaN이나 None 값이 있는 경우 건너뛰기
            if pd.isna(predicted_total) or pd.isna(actual_total):
                continue
            
            comparison_data.append({
                '환자 ID': patient_number,
                '예측 총점': round(predicted_total, 1),
                '실제 총점': round(actual_total, 1)
            })
            
        except (KeyError, TypeError, AttributeError) as e:
            # 환자 ID가 없거나 데이터가 없는 경우 삭제 (건너뛰기)
            continue
    
    # DataFrame 생성
    comparison_df = pd.DataFrame(comparison_data)
    
    if comparison_df.empty:
        print("❌ 비교할 데이터가 없습니다.")
        return
    
    # 상관계수 계산
    correlation = np.nan
    if len(comparison_df) > 1:
        try:
            from scipy.stats import pearsonr
            correlation, p_value = pearsonr(comparison_df['예측 총점'], comparison_df['실제 총점'])
        except:
            correlation = best_params['avg_correlation']
    
    # 상관계수 컬럼 추가 (첫 번째 행에만)
    comparison_df['상관계수'] = ''
    if not np.isnan(correlation):
        comparison_df.loc[0, '상관계수'] = round(correlation, 3)
    
    # Excel 파일로 저장
    output_path = '/Volumes/SSAM/aptk_model/ptk_3rd_comparison.xlsx'
    
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            comparison_df.to_excel(writer, sheet_name='PTK_3rd_Comparison', index=False)
            
            # 워크시트 가져오기
            worksheet = writer.sheets['PTK_3rd_Comparison']
            
            # 컬럼 너비 조정
            worksheet.column_dimensions['A'].width = 12
            worksheet.column_dimensions['B'].width = 12
            worksheet.column_dimensions['C'].width = 12
            worksheet.column_dimensions['D'].width = 12
        
        print(f"✅ Excel 비교 파일 저장 완료: {output_path}")
        print(f"📈 전체 환자 수: {len(comparison_df)}")
        print(f"🔗 상관계수: {correlation:.3f}" if not np.isnan(correlation) else "🔗 상관계수: 계산 불가")
        
    except Exception as e:
        print(f"❌ Excel 파일 저장 실패: {e}")
        # CSV로 대체 저장
        comparison_df.to_csv('/Volumes/SSAM/aptk_model/ptk_3rd_comparison.csv', index=False)
        print("📄 CSV 파일로 대체 저장 완료: ptk_3rd_comparison.csv")

if __name__ == "__main__":
    # 최적화 실행
    result = optimize_ptk_parameters()
    
    if result is None or result[0] is None:
        print("❌ PTK 최적화 실패: 유효한 결과가 없습니다.")
        print("   - WAV 파일 경로나 라벨 데이터를 확인하세요.")
        pass
    else:
        results_df, best_avg, best_max = result
        
        # 결과 시각화
        visualize_ptk_optimization_results(results_df)
        
        # 민감도 분석
        height_sens, distance_sens = analyze_ptk_parameter_sensitivity(results_df)
        
        # 최종 보고서 저장
        with open('/Volumes/SSAM/aptk_model/ptk_3rd_optimization_report.txt', 'w', encoding='utf-8') as f:
            f.write("🏆 PTK 파라미터 최적화 보고서\n")
            f.write("="*60 + "\n\n")
            
            f.write("📊 평균 상관계수 기준 최적 결과:\n")
            f.write(f"최고 평균 상관계수: {best_avg['avg_correlation']:.6f}\n")
            f.write(f"최적 height: {best_avg['height']:.3f}\n")
            f.write(f"최적 distance: {int(best_avg['distance'])}\n")
            f.write(f"유효 샘플 수: {int(best_avg['valid_samples'])}\n")
            f.write(f"처리 시간: {best_avg['elapsed_time']:.2f}초\n\n")
            
            f.write("🎯 개별 열별 상관계수 (평균 기준):\n")
            for col in ['peo_3rd', 'keo_3rd']:
                if f'{col}_correlation' in best_avg:
                    f.write(f"  {col}: {best_avg[f'{col}_correlation']:.4f}\n")
            f.write("\n")
            
            f.write("📊 최대 상관계수 기준 최적 결과:\n")
            f.write(f"최고 최대 상관계수: {best_max['max_correlation']:.6f}\n")
            f.write(f"최적 height: {best_max['height']:.3f}\n")
            f.write(f"최적 distance: {int(best_max['distance'])}\n\n")
            f.write(f"최적 n: {int(best_max['n'])}\n\n")

            
            f.write("📊 상위 10개 결과 (평균 상관계수 기준):\n")
            f.write("-"*40 + "\n")
            top_10 = results_df.nlargest(10, 'avg_correlation')
            for idx, (_, row) in enumerate(top_10.iterrows(), 1):
                f.write(f"{idx:2d}. 평균 상관계수: {row['avg_correlation']:.4f} | "
                       f"height: {row['height']:.3f} | "
                       f"distance: {int(row['distance'])}\n")
        
        print("\n💾 최종 보고서 저장 완료: /Volumes/SSAM/aptk_model/ptk_3rd_optimization_report.txt")
        
        # Excel 비교 파일 생성
        try:
            create_excel_comparison(results_df, best_avg)
        except Exception as e:
            print(f"⚠️ Excel 파일 생성 중 오류: {e}")
        
        print("🎉 PTK 최적화 파이프라인 완료!")