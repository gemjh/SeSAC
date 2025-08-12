import streamlit as st
import os

# TensorFlow 환경 설정
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['OMP_NUM_THREADS'] = '1'

st.title("TensorFlow Test App")
st.write("Docker 환경에서 TensorFlow 테스트")

if 'tf_loaded' not in st.session_state:
    with st.spinner('TensorFlow 로딩 중...'):
        try:
            import tensorflow as tf
            tf.config.threading.set_intra_op_parallelism_threads(1)
            tf.config.threading.set_inter_op_parallelism_threads(1)
            st.session_state.tf_loaded = True
            st.session_state.tf_version = tf.__version__
            st.success(f'TensorFlow 로딩 완료! 버전: {tf.__version__}')
        except Exception as e:
            st.error(f'TensorFlow 로딩 실패: {e}')
            st.session_state.tf_loaded = False

if st.session_state.get('tf_loaded', False):
    st.write(f"현재 TensorFlow 버전: {st.session_state.tf_version}")
    
    if st.button("간단한 연산 테스트"):
        import tensorflow as tf
        a = tf.constant([1, 2, 3])
        b = tf.constant([4, 5, 6])
        result = tf.add(a, b)
        st.write(f"결과: {result.numpy()}")