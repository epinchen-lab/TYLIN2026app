import streamlit as st
import google.generativeai as genai

# --- 頁面設定 ---
st.set_page_config(page_title="烏龍派出所風格產生器", page_icon="👮‍♂️", layout="centered")

st.title("👮‍♂️ 烏龍派出所 (Kochikame) 風格轉繪")
st.markdown("上傳照片，AI 自動幫你轉換成兩津勘吉風格的描述與指令！")

# --- 側邊欄：設定 API Key ---
st.sidebar.header("第一步：設定")
api_key = st.sidebar.text_input("輸入你的 Google API Key", type="password")

# --- 主畫面邏輯 ---
if api_key:
    try:
        # 設定 API
        genai.configure(api_key=api_key)
        
        # --- 自動抓取可用模型 (解決 404 問題的關鍵) ---
        # 找出所有支援 "generateContent" (圖文生成) 的模型
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        # 讓使用者從選單中選擇模型 (預設選第一個)
        if available_models:
            st.sidebar.header("第二步：選擇模型")
            # 優先嘗試選取 gemini-1.5-flash 或 gemini-1.5-pro
            default_index = 0
            for i, name in enumerate(available_models):
                if "gemini-1.5-flash" in name:
                    default_index = i
                    break
            
            selected_model_name = st.sidebar.selectbox("偵測到你的帳號可用模型：", available_models, index=default_index)
            
            # --- 上傳圖片區域 ---
            uploaded_file = st.file_uploader("第三步：上傳照片 (JPG/PNG)", type=["jpg", "png", "jpeg"])

            if uploaded_file:
                st.image(uploaded_file, caption="原始照片", use_column_width=True)
                
                if st.button("🚀 開始轉繪分析"):
                    with st.spinner(f'正在使用 {selected_model_name} 進行分析...'):
                        try:
                            # 使用使用者選單選到的模型
                            model = genai.GenerativeModel(selected_model_name)
                            
                            bytes_data = uploaded_file.getvalue()
                            image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
                            
                            prompt = """
                            You are an expert art director. Analyze this image and write a detailed text-to-image prompt to recreate this scene in the specific style of "Kochira Katsushika-ku Kameari Kōen-mae Hashutsujo" (Kochikame).
                            Follow these rules:
                            1. Art Style: Osamu Akimoto style, 90s anime aesthetic, bold thick black outlines, cel-shaded, flat vibrant colors.
                            2. Character Conversion: Identify main subjects. If there is a bald/older man, exaggerate him to look like Ryotsu Kankichi (thick unibrow). If handsome men/women, render in 90s anime style.
                            3. Output ONLY the English prompt.
                            """
                            
                            response = model.generate_content([prompt, image_parts[0]])
                            
                            st.success("分析完成！請複製下方的指令：")
                            st.code(response.text, language="markdown")
                            st.markdown("### 接下來怎麼做？")
                            st.info("由於這是「純文字生成」版本，請複製上面的英文指令，貼到 [Bing Image Creator](https://www.bing.com/images/create) 即可得到圖片！")

                        except Exception as e:
                            st.error(f"生成過程發生錯誤：{e}")
        else:
            st.error("⚠️ 你的 API Key 有效，但在這個專案中找不到可用的模型。請確認 Google AI Studio 中是否已啟用 Gemini API。")

    except Exception as e:
        st.error(f"API Key 驗證失敗：{e}")

elif not api_key:
    st.warning("👈 請先在左側欄位輸入你的 Google API Key")