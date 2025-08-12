import optuna
filepath = "/Users/kimberlyjojohirn/Downloads/SeSAC/project/spice/0_아/p_1_1.wav"
labeled_dataset=


def analyze_pitch_stability(filepath, std_threshold=1.5, confidence_threshold=0.4, window_size=5):
    """SPICE 전용 피치 안정성 분석 파이프라인"""
    print(f"------------------------------------------------------------------------\n\n\n현재 설정: std_threshold = {std_threshold}, confidence_threshold = {confidence_threshold}, window_size = {window_size} \n\n\n------------------------------------------------------------------------")

    try:
        # 1. 오디오 로드
        audio, sr = load_audio(filepath)
        actual_duration = len(audio) / sr
        
        # 2. SPICE로 피치 추정
        pitch, confidence = estimate_pitch_spice_only(audio, sr)
        
        # 3. 피치 필터링
        filtered_pitch = filter_pitch(pitch, confidence, threshold=confidence_threshold)
        
        # 4. 안정성 평가
        def custom_moving_std(seq, win):
            if len(seq) == 0:
                return []
            padded = np.pad(seq, (win//2,), mode='edge')
            std_values = []
            for i in range(len(seq)):
                window = padded[i:i+win]
                valid_values = window[window > 0]
                if len(valid_values) > 1:
                    std_values.append(np.std(valid_values))
                else:
                    std_values.append(0.0)
            return std_values
        
        pitch_std = custom_moving_std(filtered_pitch, window_size)
        mono_flags = [s < std_threshold and p > 0 for s, p in zip(pitch_std, filtered_pitch)]
        
        # 5. 결과 계산
        actual_fps = len(filtered_pitch) / actual_duration
        mono_duration = sum(mono_flags) / actual_fps

        return mono_duration
        
    except Exception as e:
        print(f"분석 실패: {e}")
        raise e

def objective(trial):
    std_threshold = trial.suggest_float("std_threshold", 0.5, 5.0)
    confidence_threshold = trial.suggest_float("confidence_threshold", 0.7, 0.99)
    window_size = trial.suggest_int("window_size", 3, 15)

    total_error = 0
    for wav_file, true_duration in labeled_dataset:
        pred_duration = run_pitch_estimator(
            wav_file,
            std_threshold=std_threshold,
            confidence_threshold=confidence_threshold,
            window_size=window_size
        )
        error = abs(pred_duration - true_duration)
        total_error += error

    return total_error / len(labeled_dataset)

study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=50)

print("Best parameters:", study.best_params)
