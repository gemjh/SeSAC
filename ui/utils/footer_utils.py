import streamlit as st
import base64

def add_footer():
    """전문적인 기업 스타일 footer 추가"""
    try:
        # 이미지를 base64로 인코딩
        with open("ui/utils/logo.jpeg", "rb") as f:
            img_data = f.read()
        img_base64 = base64.b64encode(img_data).decode()
        
        footer_html = f"""
        <style>
        .custom-footer {{
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background: linear-gradient(135deg, rgba(173, 216, 230, 0.9), rgba(135, 206, 250, 0.9));
            color: #6c757d;
            font-size: 11px;
            line-height: 1.4;
            padding: 12px 0;
            border-top: 1px solid #dee2e6;
            z-index: 999; /* 사이드바보다 위에 표시 */
            backdrop-filter: blur(10px);
        }}
        .footer-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 0 0 20px;
        }}

        .footer-left {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .footer-logo {{
            height: 50px;
            margin-left: 80px;
            width: auto;
        }}
        .footer-right {{
            text-align: right;
            font-size: 10px;
            color: #868e96;
        }}
        .footer-company {{
            font-weight: 500;
            color: #495057;
            margin-bottom: 2px;
        }}
        .footer-info {{
            margin-bottom: 1px;
        }}
        /* 메인 컨텐츠에 하단 패딩 추가 */
        .main .block-container {{
            padding-bottom: 100px !important;
        }}
        </style>
        <div class="custom-footer">
            <div class="footer-content">
                <div class="footer-left">
                    <img src="data:image/jpeg;base64,{img_base64}" alt="KellaWave Logo" class="footer-logo">
                    <div>
                        <div class="footer-company">Copyright © 2025 (주)켈라웨이브. All rights reserved.</div>
                        <div class="footer-info">AI 기반 언어치료 솔루션 CLAP | 언어재활 전문 시스템</div>
                    </div>
                </div>
                <div class="footer-right">
                    <div class="footer-info">사업자등록번호 : 000-00-00000 | 대표자 : 000</div>
                    <div class="footer-info">서울특별시 영등포구 경인로 000길 00-00 0000호 | 연락처 : 02-0000-0000</div>
                    <div class="footer-info">이메일 : info@kellawave.co.kr | 웹사이트 : www.kellawave.co.kr</div>
                </div>
            </div>
        </div>
        """
        st.markdown(footer_html, unsafe_allow_html=True)
    except Exception as e:
        print(f"Footer 로딩 실패: {e}")
        # 실패시 간단한 footer
        simple_footer = """
        <div style="position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(248,249,250,0.9); 
                    text-align: center; padding: 10px; font-size: 11px; color: #666; border-top: 1px solid #ddd; z-index: 999;">
            Copyright © 2025 (주)켈라웨이브. All rights reserved.
        </div>
        """
        st.markdown(simple_footer, unsafe_allow_html=True)