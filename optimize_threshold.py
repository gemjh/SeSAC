import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import product
import time
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# ah_sound.py의 함수들을 임포트
import sys
sys.path.append('H:/')
from ah_sound import analyze_pitch_stability

def optimize_thresholds():
    """
    가장 높은 상관계수를 찾기 위한 threshold 최적화 파이프라인
    """
    print("🔍 Threshold 최적화 파이프라인 시작...")
    
    # 최적화할 파라미터 범위 설정
    std_thresholds = np.arange(0.5, 3.1, 0.1)  # 0.5 ~ 3.0, 0.1 간격
    confidence_thresholds = np.arange(0.1, 0.9, 0.05)  # 0.1 ~ 0.85, 0.05 간격
    window_sizes = [3, 5, 7, 9, 11]  # 다양한 윈도우 크기
    
    print(f"📊 테스트할 조합 수: {len(std_thresholds) * len(confidence_thresholds) * len(window_sizes)}")
    
    # 기본 데이터 로드
    folder = r'C:\Users\user\Downloads\data'
    pattern = os.path.join(folder, '**', 'CLAP_D', '0', 'p*.wav')
    wav_files = glob.glob(pattern, recursive=True)
    print(f"🎵 발견된 WAV 파일 수: {len(wav_files)}")
    
    # 라벨 데이터 로드
    df = pd.read_csv(r'H:\labeled_data_D.csv', header=1, index_col=0)
    label = df.loc[:, 'ah_1st_sec':'ptk_ave..1']
    ah_label = label.loc[:, 'ah_1st_sec':'ah_2nd_sec']
    
    # 최적화 결과를 저장할 리스트
    optimization_results = []
    
    # 전체 조합 수 계산
    total_combinations = len(std_thresholds) * len(confidence_thresholds) * len(window_sizes)
    
    print("🚀 최적화 시작...")
    
    # 진행 상황을 추적하기 위한 카운터
    combination_count = 0
    
    for std_thresh in std_thresholds:
        for conf_thresh in confidence_thresholds:
            for win_size in window_sizes:
                combination_count += 1
                
                print(f"\n📈 진행률: {combination_count}/{total_combinations} "
                      f"({combination_count/total_combinations*100:.1f}%)")
                print(f"🎯 현재 테스트: std={std_thresh:.2f}, conf={conf_thresh:.2f}, win={win_size}")
                
                try:
                    start_time = time.time()
                    
                    # 현재 파라미터로 결과 계산
                    ah_result = pd.DataFrame(columns=['ah_1st_sec', 'ah_2nd_sec'])
                    
                    for wav_file in wav_files:
                        # Windows 경로 처리를 위해 replace를 수정
                        parts = wav_file.replace(folder, '').strip(os.sep).split(os.sep)
                        if len(parts) > 0:
                            index_key = parts[0]
                        else:
                            index_key = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(wav_file))))
                        
                        if index_key not in ah_result.index:
                            ah_result.loc[index_key] = [None, None]
                        
                        filename = os.path.basename(wav_file)
                        if 'p_1_' in filename:
                            try:
                                result = analyze_pitch_stability(
                                    wav_file, 
                                    std_threshold=std_thresh,
                                    confidence_threshold=conf_thresh,
                                    window_size=win_size
                                )
                                ah_result.loc[index_key, 'ah_1st_sec'] = result
                            except Exception as e:
                                print(f"⚠️  파일 처리 오류 {wav_file}: {e}")
                                continue
                    
                    # 결과가 있는지 확인
                    if ah_result['ah_1st_sec'].dropna().empty:
                        print("❌ 분석 결과가 없습니다.")
                        continue
                    
                    # 상관계수 계산
                    ah_result.index = ah_result.index.astype(int)
                    combined = pd.concat([
                        ah_result['ah_1st_sec'].rename('ah_1st_sec_result'),
                        ah_label['ah_1st_sec']
                    ], axis=1, join="inner")
                    
                    # 유효한 데이터가 있는지 확인
                    if combined.dropna().empty or len(combined.dropna()) < 2:
                        print("❌ 상관계수 계산을 위한 충분한 데이터가 없습니다.")
                        continue
                    
                    corr_matrix = combined.corr()
                    correlation = corr_matrix.loc['ah_1st_sec_result', 'ah_1st_sec']
                    
                    # NaN 체크
                    if pd.isna(correlation):
                        print("❌ 상관계수가 NaN입니다.")
                        continue
                    
                    elapsed_time = time.time() - start_time
                    
                    # 결과 저장
                    optimization_results.append({
                        'std_threshold': std_thresh,
                        'confidence_threshold': conf_thresh,
                        'window_size': win_size,
                        'correlation': correlation,
                        'elapsed_time': elapsed_time,
                        'valid_samples': len(combined.dropna())
                    })
                    
                    print(f"✅ 상관계수: {correlation:.4f}, 처리시간: {elapsed_time:.2f}초")
                    
                except Exception as e:
                    print(f"❌ 오류 발생: {e}")
                    continue
    
    # 결과를 DataFrame으로 변환
    results_df = pd.DataFrame(optimization_results)
    
    if results_df.empty:
        print("❌ 최적화 결과가 없습니다.")
        return None
    
    # 결과 저장
    results_df.to_csv('H:/threshold_optimization_results.csv', index=False)
    print(f"💾 결과 저장 완료: H:/threshold_optimization_results.csv")
    
    # 최고 상관계수 찾기
    best_result = results_df.loc[results_df['correlation'].idxmax()]
    
    print("\n🏆 최적화 결과:")
    print("="*50)
    print(f"최고 상관계수: {best_result['correlation']:.6f}")
    print(f"최적 std_threshold: {best_result['std_threshold']:.2f}")
    print(f"최적 confidence_threshold: {best_result['confidence_threshold']:.2f}")
    print(f"최적 window_size: {int(best_result['window_size'])}")
    print(f"유효 샘플 수: {int(best_result['valid_samples'])}")
    print(f"처리 시간: {best_result['elapsed_time']:.2f}초")
    print("="*50)
    
    return results_df, best_result

def visualize_optimization_results(results_df):
    """
    최적화 결과를 시각화
    """
    print("📊 결과 시각화 중...")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. 상관계수 히스토그램
    axes[0, 0].hist(results_df['correlation'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0, 0].set_xlabel('Correlation Coefficient')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('Distribution of Correlation Coefficients')
    axes[0, 0].axvline(results_df['correlation'].max(), color='red', linestyle='--', 
                       label=f'Max: {results_df["correlation"].max():.4f}')
    axes[0, 0].legend()
    
    # 2. std_threshold vs correlation
    scatter = axes[0, 1].scatter(results_df['std_threshold'], results_df['correlation'], 
                                c=results_df['confidence_threshold'], cmap='viridis', alpha=0.6)
    axes[0, 1].set_xlabel('STD Threshold')
    axes[0, 1].set_ylabel('Correlation Coefficient')
    axes[0, 1].set_title('STD Threshold vs Correlation (colored by Confidence Threshold)')
    plt.colorbar(scatter, ax=axes[0, 1], label='Confidence Threshold')
    
    # 3. confidence_threshold vs correlation
    scatter2 = axes[1, 0].scatter(results_df['confidence_threshold'], results_df['correlation'], 
                                 c=results_df['window_size'], cmap='plasma', alpha=0.6)
    axes[1, 0].set_xlabel('Confidence Threshold')
    axes[1, 0].set_ylabel('Correlation Coefficient')
    axes[1, 0].set_title('Confidence Threshold vs Correlation (colored by Window Size)')
    plt.colorbar(scatter2, ax=axes[1, 0], label='Window Size')
    
    # 4. Top 10 결과
    top_10 = results_df.nlargest(10, 'correlation')
    axes[1, 1].barh(range(len(top_10)), top_10['correlation'])
    axes[1, 1].set_yticks(range(len(top_10)))
    axes[1, 1].set_yticklabels([f"std:{row['std_threshold']:.1f}, conf:{row['confidence_threshold']:.2f}, win:{int(row['window_size'])}" 
                               for _, row in top_10.iterrows()])
    axes[1, 1].set_xlabel('Correlation Coefficient')
    axes[1, 1].set_title('Top 10 Parameter Combinations')
    
    plt.tight_layout()
    plt.savefig('H:/threshold_optimization_visualization.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 3D 시각화 (선택적)
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    scatter = ax.scatter(results_df['std_threshold'], 
                        results_df['confidence_threshold'], 
                        results_df['correlation'],
                        c=results_df['window_size'], 
                        cmap='coolwarm', 
                        s=50, 
                        alpha=0.6)
    
    ax.set_xlabel('STD Threshold')
    ax.set_ylabel('Confidence Threshold')
    ax.set_zlabel('Correlation Coefficient')
    ax.set_title('3D Optimization Results')
    plt.colorbar(scatter, label='Window Size')
    
    plt.savefig('H:/threshold_optimization_3d.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("💾 시각화 결과 저장 완료:")
    print("  - H:/threshold_optimization_visualization.png")
    print("  - H:/threshold_optimization_3d.png")

def analyze_parameter_sensitivity(results_df):
    """
    각 파라미터의 민감도 분석
    """
    print("🔬 파라미터 민감도 분석...")
    
    # 각 파라미터별 평균 상관계수
    std_sensitivity = results_df.groupby('std_threshold')['correlation'].agg(['mean', 'std', 'count'])
    conf_sensitivity = results_df.groupby('confidence_threshold')['correlation'].agg(['mean', 'std', 'count'])
    win_sensitivity = results_df.groupby('window_size')['correlation'].agg(['mean', 'std', 'count'])
    
    # 결과 출력
    print("\n📈 STD Threshold 민감도:")
    print(f"최고 평균 상관계수: {std_sensitivity['mean'].max():.4f} (std_threshold: {std_sensitivity['mean'].idxmax():.2f})")
    
    print("\n📈 Confidence Threshold 민감도:")
    print(f"최고 평균 상관계수: {conf_sensitivity['mean'].max():.4f} (confidence_threshold: {conf_sensitivity['mean'].idxmax():.2f})")
    
    print("\n📈 Window Size 민감도:")
    print(f"최고 평균 상관계수: {win_sensitivity['mean'].max():.4f} (window_size: {int(win_sensitivity['mean'].idxmax())})")
    
    # 민감도 시각화
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # STD Threshold
    axes[0].errorbar(std_sensitivity.index, std_sensitivity['mean'], 
                     yerr=std_sensitivity['std'], capsize=3, marker='o')
    axes[0].set_xlabel('STD Threshold')
    axes[0].set_ylabel('Mean Correlation')
    axes[0].set_title('STD Threshold Sensitivity')
    axes[0].grid(True, alpha=0.3)
    
    # Confidence Threshold
    axes[1].errorbar(conf_sensitivity.index, conf_sensitivity['mean'], 
                     yerr=conf_sensitivity['std'], capsize=3, marker='s')
    axes[1].set_xlabel('Confidence Threshold')
    axes[1].set_ylabel('Mean Correlation')
    axes[1].set_title('Confidence Threshold Sensitivity')
    axes[1].grid(True, alpha=0.3)
    
    # Window Size
    axes[2].errorbar(win_sensitivity.index, win_sensitivity['mean'], 
                     yerr=win_sensitivity['std'], capsize=3, marker='^')
    axes[2].set_xlabel('Window Size')
    axes[2].set_ylabel('Mean Correlation')
    axes[2].set_title('Window Size Sensitivity')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('H:/parameter_sensitivity_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return std_sensitivity, conf_sensitivity, win_sensitivity

if __name__ == "__main__":
    # 최적화 실행
    results_df, best_result = optimize_thresholds()
    
    if results_df is not None and not results_df.empty:
        # 결과 시각화
        visualize_optimization_results(results_df)
        
        # 민감도 분석
        std_sens, conf_sens, win_sens = analyze_parameter_sensitivity(results_df)
        
        # 최종 보고서 저장
        with open('H:/optimization_report.txt', 'w', encoding='utf-8') as f:
            f.write("🏆 Threshold 최적화 보고서\n")
            f.write("="*50 + "\n\n")
            f.write(f"최고 상관계수: {best_result['correlation']:.6f}\n")
            f.write(f"최적 std_threshold: {best_result['std_threshold']:.2f}\n")
            f.write(f"최적 confidence_threshold: {best_result['confidence_threshold']:.2f}\n")
            f.write(f"최적 window_size: {int(best_result['window_size'])}\n")
            f.write(f"유효 샘플 수: {int(best_result['valid_samples'])}\n")
            f.write(f"처리 시간: {best_result['elapsed_time']:.2f}초\n\n")
            
            f.write("📊 상위 10개 결과:\n")
            f.write("-"*30 + "\n")
            top_10 = results_df.nlargest(10, 'correlation')
            for idx, (_, row) in enumerate(top_10.iterrows(), 1):
                f.write(f"{idx:2d}. 상관계수: {row['correlation']:.4f} | "
                       f"std: {row['std_threshold']:.2f} | "
                       f"conf: {row['confidence_threshold']:.2f} | "
                       f"win: {int(row['window_size'])}\n")
        
        print("\n💾 최종 보고서 저장 완료: H:/optimization_report.txt")
        print("🎉 최적화 파이프라인 완료!")
    else:
        print("❌ 최적화 실패: 유효한 결과가 없습니다.")