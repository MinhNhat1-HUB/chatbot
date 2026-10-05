import streamlit as st
import google.generativeai as genai

# ==========================================
# CẤU HÌNH TRANG VÀ CSS
# ==========================================
st.set_page_config(page_title="Chatbot AI Cá Nhân", page_icon="🤖", layout="centered")

st.markdown("""
<style>
    /* Ép tin nhắn của người dùng sang bên phải */
    [data-testid="stChatMessage"][data-baseweb="block"]:has(div:contains("user")) {
        flex-direction: row-reverse;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
st.title("🤖 Chatbot AI Cá Nhân")
st.markdown("Xây dựng bằng Python, Streamlit và **Gemini API**")

with st.sidebar:
    st.header("⚙️ Cấu hình hệ thống")
    api_key = st.text_input("Nhập Gemini API Key của bạn:", type="password")
    st.divider()
    if st.button("🗑️ Xóa lịch sử trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# QUẢN LÝ LỊCH SỬ CHAT (Định dạng chuẩn của Gemini)
# ==========================================
if "messages" not in st.session_state:
    # Lời chào ban đầu (Gemini dùng "model" thay vì "assistant")
    st.session_state.messages = [
        {"role": "model", "parts": ["Xin chào! Tôi là trợ lý AI (Gemini). Tôi có thể giúp gì cho bạn hôm nay?"]}
    ]

# Hiển thị lại toàn bộ lịch sử lên màn hình
for message in st.session_state.messages:
    role_ui = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(role_ui):
        st.markdown(message["parts"][0])

# ==========================================
# XỬ LÝ NHẬP LIỆU & GỌI API GEMINI
# ==========================================
if prompt := st.chat_input("Nhập tin nhắn của bạn vào đây..."):
    
    # 1. In câu hỏi của User ra màn hình & lưu vào session
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    
    # Kiểm tra Key
    if not api_key:
        st.error("⚠️ Vui lòng nhập API Key ở menu bên trái để bắt đầu trò chuyện.")
        st.stop()
        
    try:
        # 2. Cấu hình chìa khóa API
        genai.configure(api_key=api_key)
        
        # SỬA LỖI Ở ĐÂY: Sử dụng model mới nhất (gemini-3.5-flash) thay vì bản cũ
        model = genai.GenerativeModel("gemini-3.5-flash")
        
        # 3. Gọi AI trả lời và tạo hiệu ứng gõ chữ (Streaming)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Đưa toàn bộ lịch sử vào để Bot nhớ ngữ cảnh
            response = model.generate_content(st.session_state.messages, stream=True)
            
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
                
            message_placeholder.markdown(full_response)
            
        # 4. Lưu câu trả lời của Bot vào lịch sử
        st.session_state.messages.append({"role": "model", "parts": [full_response]})
        
    except Exception as e:
        # Bắt mọi lỗi xảy ra để app không bị sập
        st.error(f"❌ Đã xảy ra lỗi từ máy chủ: {str(e)}")