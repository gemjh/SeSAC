"""
모든 PTK 최적화 방식을 실행하고 결과 비교
"""
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_all_optimizations():
    """모든 최적화 방식 실행 및 결과 비교"""
    print("🚀 모든 PTK 최적화 방식 실행 시작...")
    print("="*80)
    
    results_summary = {}
    execution_times = {}
    
    # 1. 직접 로드 방식
    print("\n1️⃣ 직접 로드 방식 실행 중...")
    try:
        start_time = time.time()
        exec(open('H:/optimize_ptk_v2_direct.py').read(), globals())
        result_direct = optimize_ptk_direct()
        execution_times['direct'] = time.time() - start_time
        
        if result_direct[0] is not None:
            results_df_direct, best_avg_direct, best_max_direct = result_direct
            results_summary['direct'] = {
                'method': '직접 로드',
                'avg_correlation': best_avg_direct['avg_correlation'],
                'max_correlation': best_max_direct['max_correlation'],
                'best_height': best_avg_direct['height'],
                'best_distance': best_avg_direct['distance'],
                'execution_time': execution_times['direct'],
                'total_combinations': len(results_df_direct)
            }
            print(f"✅ 직접 로드 완료: 평균 상관계수 {best_avg_direct['avg_correlation']:.6f}")
        else:
            print("❌ 직접 로드 방식 실패")
            
    except Exception as e:
        print(f"❌ 직접 로드 방식 오류: {e}")
    
    # 2. 캐싱 방식
    print("\n2️⃣ 캐싱 방식 실행 중...")
    try:
        start_time = time.time()
        exec(open('H:/optimize_ptk_v2_cached.py').read(), globals())
        result_cached = optimize_ptk_cached()
        execution_times['cached'] = time.time() - start_time
        
        if result_cached[0] is not None:
            results_df_cached, best_avg_cached, best_max_cached = result_cached
            results_summary['cached'] = {
                'method': '캐싱 사용',
                'avg_correlation': best_avg_cached['avg_correlation'],
                'max_correlation': best_max_cached['max_correlation'],
                'best_height': best_avg_cached['height'],
                'best_distance': best_avg_cached['distance'],
                'execution_time': execution_times['cached'],
                'total_combinations': len(results_df_cached)
            }
            print(f"✅ 캐싱 방식 완료: 평균 상관계수 {best_avg_cached['avg_correlation']:.6f}")
        else:
            print("❌ 캐싱 방식 실패")
            
    except Exception as e:
        print(f"❌ 캐싱 방식 오류: {e}")
    
    # 3. 원본 정확 매치 방식
    print("\n3️⃣ 원본 정확 매치 방식 실행 중...")
    try:
        start_time = time.time()
        exec(open('H:/optimize_ptk_v2_exact.py').read(), globals())
        result_exact = optimize_ptk_exact()
        execution_times['exact'] = time.time() - start_time
        
        if result_exact[0] is not None:
            results_df_exact, best_avg_exact, best_max_exact = result_exact
            results_summary['exact'] = {
                'method': '원본 정확 매치',
                'avg_correlation': best_avg_exact['avg_correlation'],
                'max_correlation': best_max_exact['max_correlation'],
                'best_height': best_avg_exact['height'],
                'best_distance': best_avg_exact['distance'],
                'execution_time': execution_times['exact'],
                'total_combinations': len(results_df_exact)
            }
            
            # 원본 파라미터 결과도 포함
            original_result = results_df_exact[results_df_exact['is_original'] == True]
            if not original_result.empty:
                orig = original_result.iloc[0]
                results_summary['exact']['original_avg'] = orig['avg_correlation']
                results_summary['exact']['original_max'] = orig['max_correlation']
            
            print(f"✅ 원본 정확 매치 완료: 평균 상관계수 {best_avg_exact['avg_correlation']:.6f}")
        else:
            print("❌ 원본 정확 매치 방식 실패")
            
    except Exception as e:
        print(f"❌ 원본 정확 매치 방식 오류: {e}")
    
    # 결과 요약 및 비교
    print("\n" + "="*80)
    print("📊 전체 결과 요약 및 비교")
    print("="*80)
    
    if results_summary:
        # 결과를 DataFrame으로 변환
        summary_df = pd.DataFrame.from_dict(results_summary, orient='index')
        
        # 정렬 (평균 상관계수 기준)
        summary_df = summary_df.sort_values('avg_correlation', ascending=False)
        
        print("\n🏆 방식별 성능 순위:")
        print("-" * 80)
        for i, (method, row) in enumerate(summary_df.iterrows(), 1):
            print(f"{i}. {row['method']}:")
            print(f"   평균 상관계수: {row['avg_correlation']:.6f}")
            print(f"   최대 상관계수: {row['max_correlation']:.6f}")
            print(f"   최적 파라미터: height={row['best_height']:.3f}, distance={int(row['best_distance'])}")
            print(f"   실행 시간: {row['execution_time']:.2f}초")
            print(f"   테스트 조합 수: {int(row['total_combinations'])}")
            
            if 'original_avg' in row and not pd.isna(row['original_avg']):
                print(f"   원본 파라미터 결과: {row['original_avg']:.6f}")
                improvement = ((row['avg_correlation'] - row['original_avg']) / row['original_avg'] * 100)
                print(f"   원본 대비 개선: {improvement:+.2f}%")
            print()
        
        # 결과 저장
        summary_df.to_csv('H:/ptk_optimization_comparison.csv', index=True)
        
        # 시각화
        visualize_comparison(summary_df)
        
        # 최종 결론
        best_method = summary_df.iloc[0]
        print("🎉 최종 결론:")
        print(f"✨ 최고 성능: {best_method['method']}")
        print(f"✨ 최고 평균 상관계수: {best_method['avg_correlation']:.6f}")
        print(f"✨ 최적 파라미터: height={best_method['best_height']:.3f}, distance={int(best_method['best_distance'])}")
        
        return summary_df
    
    else:
        print("❌ 모든 방식이 실패했습니다.")
        return None

def visualize_comparison(summary_df):
    """결과 비교 시각화"""
    print("📊 결과 시각화 중...")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    methods = summary_df['method'].values
    avg_corrs = summary_df['avg_correlation'].values
    max_corrs = summary_df['max_correlation'].values
    exec_times = summary_df['execution_time'].values
    
    # 1. 평균 상관계수 비교
    bars1 = axes[0, 0].bar(methods, avg_corrs, color='skyblue', alpha=0.8)
    axes[0, 0].set_title('평균 상관계수 비교')
    axes[0, 0].set_ylabel('평균 상관계수')
    axes[0, 0].tick_params(axis='x', rotation=45)
    for bar, value in zip(bars1, avg_corrs):
        axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                       f'{value:.4f}', ha='center', va='bottom')
    
    # 2. 최대 상관계수 비교
    bars2 = axes[0, 1].bar(methods, max_corrs, color='lightcoral', alpha=0.8)
    axes[0, 1].set_title('최대 상관계수 비교')
    axes[0, 1].set_ylabel('최대 상관계수')
    axes[0, 1].tick_params(axis='x', rotation=45)
    for bar, value in zip(bars2, max_corrs):
        axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                       f'{value:.4f}', ha='center', va='bottom')
    
    # 3. 실행 시간 비교
    bars3 = axes[1, 0].bar(methods, exec_times, color='lightgreen', alpha=0.8)
    axes[1, 0].set_title('실행 시간 비교')
    axes[1, 0].set_ylabel('실행 시간 (초)')
    axes[1, 0].tick_params(axis='x', rotation=45)
    for bar, value in zip(bars3, exec_times):
        axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(exec_times)*0.01,
                       f'{value:.1f}s', ha='center', va='bottom')
    
    # 4. 최적 파라미터 분포
    heights = summary_df['best_height'].values
    distances = summary_df['best_distance'].values
    scatter = axes[1, 1].scatter(heights, distances, c=avg_corrs, cmap='viridis', s=100, alpha=0.8)
    axes[1, 1].set_xlabel('Height')
    axes[1, 1].set_ylabel('Distance')
    axes[1, 1].set_title('최적 파라미터 분포')
    plt.colorbar(scatter, ax=axes[1, 1], label='평균 상관계수')
    
    for i, method in enumerate(methods):
        axes[1, 1].annotate(method, (heights[i], distances[i]), 
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('H:/ptk_optimization_methods_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("💾 비교 시각화 저장 완료: H:/ptk_optimization_methods_comparison.png")

if __name__ == "__main__":
    try:
        summary_df = run_all_optimizations()
        
        # 최종 보고서 작성
        if summary_df is not None:
            with open('H:/ptk_optimization_final_report.txt', 'w', encoding='utf-8') as f:
                f.write("🏆 PTK 파라미터 최적화 최종 보고서\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("📊 실행된 최적화 방식:\n")
                f.write("1. 직접 로드 방식 - librosa로 직접 로드\n")
                f.write("2. 캐싱 사용 방식 - 전처리 결과 캐싱\n")
                f.write("3. 원본 정확 매치 - ptk_sound.py와 동일한 구현\n\n")
                
                f.write("🏆 성능 순위:\n")
                f.write("-" * 40 + "\n")
                for i, (method, row) in enumerate(summary_df.iterrows(), 1):
                    f.write(f"{i}. {row['method']}\n")
                    f.write(f"   평균 상관계수: {row['avg_correlation']:.6f}\n")
                    f.write(f"   최대 상관계수: {row['max_correlation']:.6f}\n")
                    f.write(f"   최적 파라미터: height={row['best_height']:.3f}, distance={int(row['best_distance'])}\n")
                    f.write(f"   실행 시간: {row['execution_time']:.2f}초\n\n")
                
                best_method = summary_df.iloc[0]
                f.write("🎉 최종 권장사항:\n")
                f.write(f"✨ 최고 성능 방식: {best_method['method']}\n")
                f.write(f"✨ 권장 파라미터: height={best_method['best_height']:.3f}, distance={int(best_method['best_distance'])}\n")
                f.write(f"✨ 예상 평균 상관계수: {best_method['avg_correlation']:.6f}\n")
        
        print("\n💾 최종 보고서 저장 완료: H:/ptk_optimization_final_report.txt")
        print("🎉 전체 최적화 과정 완료!")
        
    except Exception as e:
        print(f"❌ 전체 실행 오류: {e}")
        import traceback
        traceback.print_exc()