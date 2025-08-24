import numpy as np
import librosa
import scipy.signal
import matplotlib.pyplot as plt
from pydub import AudioSegment
import os
import glob
import pandas as pd

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

folder =r'C:\Users\user\Downloads\data'
pattern = os.path.join(folder, '**', 'CLAP_D', '1', 'p*.wav')
wav_files = glob.glob(pattern, recursive=True)
df=pd.read_csv('H:\labeled_data_D.csv',header=1,index_col=0)
ptk_label=df.loc[:,['peo_2nd','teo_2nd','keo_2nd','ptk_2nd']]

ptk_result=pd.DataFrame(columns=(ptk_label.loc[:,['peo_2nd','teo_2nd','keo_2nd','ptk_2nd']].columns))

for wav_file in wav_files:
    # Windows 경로 처리를 위해 replace를 수정
    parts = wav_file.replace(folder, '').strip(os.sep).split(os.sep)
    if len(parts) > 0:
        index_key = parts[0]
    else:
        index_key = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(wav_file))))

    # DataFrame에 인덱스가 없으면 새로 추가
    if index_key not in ptk_result.index:
        ptk_result.loc[index_key] = [None, None, None, None]

    filename = os.path.basename(wav_file)
    if 'p_2_' in filename:
        # print(analyze_pitch_stability(wav_file))
        ptk_result.loc[index_key, 'peo_2nd'] = count_peaks_from_waveform(wav_file)
    elif 'p_5_' in filename:
        ptk_result.loc[index_key, 'teo_2nd'] = count_peaks_from_waveform(wav_file)
    elif 'p_7_' in filename:
        ptk_result.loc[index_key, 'keo_2nd'] = count_peaks_from_waveform(wav_file)
    elif 'p_10_' in filename:
        ptk_result.loc[index_key, 'ptk_2nd'] = round(count_peaks_from_waveform(wav_file)/3,1)

import matplotlib.pyplot as plt
import seaborn as sns
# 두 DataFrame을 열 단위로 합치기
# Convert result index to integer to match ah_label index type
ptk_result.index = ptk_result.index.astype(int)

# Calculate Pearson correlation for each column
correlation_results = {}
for col in ptk_result.columns:
    if col in ptk_label.columns:
        # Align the dataframes on index and drop NaN values for correlation calculation
        temp_combined = pd.concat([ptk_result[col], ptk_label[col]], axis=1, join="inner").dropna()
        if not temp_combined.empty:
            correlation = temp_combined.corr(method='pearson').iloc[0, 1]
            correlation_results[col] = correlation
        else:
            correlation_results[col] = None # Or np.nan, depending on desired handling of empty data


# Display the correlation results
correlation_df = pd.DataFrame.from_dict(correlation_results, orient='index', columns=['Pearson Correlation'])
print(correlation_df)