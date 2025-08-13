import numpy as np
import librosa
import scipy.signal
import matplotlib.pyplot as plt
from pydub import AudioSegment


# 파일 모노채널+정규화
def convert_audio_for_model(user_file, output_file='converted_audio_file.wav',EXPECTED_SAMPLE_RATE=16000):
    
    audio = AudioSegment.from_file(user_file)
    audio = audio.set_frame_rate(EXPECTED_SAMPLE_RATE).set_channels(1)
    audio.export(output_file, format="wav")
    return output_file

# 매우 단순 버전: 그래프 피크만 세기... '퍼'만 있다는 가정하에 제일 정확 근데 하이퍼파라미터가 문제
def count_peaks_from_waveform(filepath, height=0.05, distance=3000, plot=False):
    y, sr = librosa.load(convert_audio_for_model(filepath), sr=None)
    # n초
    y_trimmed = y[:sr * 3]

    y_trimmed = y_trimmed / np.max(np.abs(y_trimmed))

    # 피크 탐지
    peaks, _ = scipy.signal.find_peaks(y_trimmed, height=height, distance=distance)

    if plot:
        plt.figure(figsize=(12, 4))
        plt.plot(y_trimmed)
        plt.plot(peaks, y_trimmed[peaks], "rx")  # 피크 위치 표시
        plt.title(f"Detected Peaks: {len(peaks)}")
        plt.show()

    return len(peaks)