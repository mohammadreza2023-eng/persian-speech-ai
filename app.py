```python
import os
import tempfile

import streamlit as st
from transformers import pipeline
from audio_recorder_streamlit import audio_recorder
from edge_tts.communicate import Communicate


# =========================
# Page Configuration
# =========================

st.set_page_config(
    page_title="Persian Speech AI",
    page_icon="🎙️",
    layout="wide",
)


# =========================
# Session State
# =========================

if "history" not in st.session_state:
    st.session_state.history = []


# =========================
# Whisper Model
# =========================
#
# فعلاً مسیر مدل را اینجا قرار نمی‌دهیم.
# بعد از مشخص شدن روش انتقال مدل به Cloud،
# این قسمت را به مسیر/منبع واقعی مدل وصل می‌کنیم.
#

@st.cache_resource
def load_whisper_model(model_path):
    return pipeline(
        "automatic-speech-recognition",
        model=model_path,
    )


# =========================
# Sidebar - TTS Settings
# =========================

st.sidebar.title("تنظیمات صدا")

voice = st.sidebar.selectbox(
    "صدا",
    [
        "fa-IR-DilaraNeural",
        "fa-IR-FaridNeural",
    ],
)

rate = st.sidebar.slider(
    "سرعت",
    -50,
    50,
    0,
    format="%d%%",
)

pitch = st.sidebar.slider(
    "زیر و بم صدا",
    -50,
    50,
    0,
    format="%dHz",
)

volume = st.sidebar.slider(
    "بلندی صدا",
    -50,
    50,
    0,
    format="%d%%",
)


# =========================
# Main Title
# =========================

st.title("🎙️ Persian Speech AI")
st.caption("تبدیل گفتار به متن و متن به گفتار")


# =========================
# Tabs
# =========================

tab_stt, tab_tts = st.tabs(
    [
        "🎙️ گفتار → متن",
        "🔊 متن → گفتار",
    ]
)


# ============================================================
# TAB 1 — Speech To Text
# ============================================================

with tab_stt:

    st.header("🎙️ تبدیل گفتار به متن")

    input_type = st.radio(
        "روش وارد کردن صدا",
        [
            "آپلود فایل صوتی",
            "ضبط با میکروفون",
        ],
        horizontal=True,
    )


    # --------------------------------------------------------
    # Upload Audio
    # --------------------------------------------------------

    if input_type == "آپلود فایل صوتی":

        audio_file = st.file_uploader(
            "فایل صوتی را انتخاب کنید",
            type=[
                "mp3",
                "wav",
                "m4a",
                "ogg",
            ],
        )

        if audio_file:

            st.audio(
                audio_file,
                format=audio_file.type,
            )

            if st.button(
                "تبدیل به متن",
                key="upload_to_text",
            ):

                st.info(
                    "مدل Whisper پس از اتصال به Cloud در این قسمت اجرا خواهد شد."
                )

                st.warning(
                    "مدل Whisper هنوز روی سرور قرار نگرفته است."
                )


    # --------------------------------------------------------
    # Browser Microphone
    # --------------------------------------------------------

    else:

        st.write(
            "برای شروع ضبط، روی دکمه میکروفون کلیک کنید."
        )

        audio = audio_recorder(
            text="",
            pause_threshold=3.0,
        )

        if audio:

            st.audio(
                audio,
                format="audio/wav",
            )

            if st.button(
                "تبدیل صدای ضبط‌شده به متن",
                key="microphone_to_text",
            ):

                st.info(
                    "مدل Whisper پس از اتصال به Cloud در این قسمت اجرا خواهد شد."
                )

                st.warning(
                    "مدل Whisper هنوز روی سرور قرار نگرفته است."
                )


# ============================================================
# TAB 2 — Text To Speech
# ============================================================

with tab_tts:

    st.header("🔊 تبدیل متن به گفتار")

    text_file = st.file_uploader(
        "فایل متنی را انتخاب کنید",
        type=["txt"],
        key="tts_file",
    )

    text_input = st.text_area(
        "متن را وارد کنید",
        height=300,
    )

    if st.button(
        "تبدیل به ویس",
        key="text_to_speech",
    ):

        if text_file:

            text = text_file.read().decode(
                "utf-8"
            )

        else:

            text = text_input


        if not text.strip():

            st.warning(
                "لطفاً متن وارد کنید یا یک فایل متنی آپلود کنید."
            )

            st.stop()


        progress = st.progress(
            0,
            text="در حال آماده‌سازی..."
        )

        try:

            progress.progress(
                30,
                text="در حال ساخت صدا..."
            )

            communicate = Communicate(
                text=text,
                voice=voice,
                rate=f"{rate:+d}%",
                volume=f"{volume:+d}%",
                pitch=f"{pitch:+d}Hz",
            )

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp3",
            ) as temp_file:

                output_path = temp_file.name


            progress.progress(
                70,
                text="در حال تولید فایل صوتی..."
            )

            communicate.save_sync(
                output_path
            )


            progress.progress(
                100,
                text="انجام شد!"
            )

            st.audio(
                output_path,
                format="audio/mp3",
            )


            st.download_button(
                "⬇️ دانلود فایل صوتی",
                data=open(
                    output_path,
                    "rb",
                ).read(),
                file_name="output.mp3",
                mime="audio/mpeg",
            )


            st.session_state.history.append(
                {
                    "type": "TTS",
                    "text": text,
                }
            )


        except Exception as e:

            st.error(
                f"خطا در تبدیل متن به گفتار:\n{e}"
            )


# ============================================================
# History
# ============================================================

with st.expander("📜 تاریخچه"):

    if not st.session_state.history:

        st.write(
            "هنوز موردی ثبت نشده است."
        )

    else:

        for i, item in enumerate(
            reversed(st.session_state.history),
            start=1,
        ):

            st.write(
                f"**{i}. {item['type']}**"
            )

            st.write(
                item["text"]
            )

            st.divider()
```

### `requirements.txt`

این فایل را هم دقیقاً به این شکل قرار بده:



