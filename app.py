import os
import tempfile

import streamlit as st
import sounddevice as sd

from transformers import pipeline
from audio_recorder_streamlit import audio_recorder
from edge_tts.communicate import Communicate


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Speech & Voice AI",
    page_icon="🎙️",
    layout="wide",
)


# =========================================================
# MODEL PATHS
# =========================================================

WHISPER_MODEL = r"C:\Users\Mohammad\Desktop\streamlit-project\Model\whisper-persian-v4"


# =========================================================
# WHISPER MODEL
# =========================================================

@st.cache_resource
def load_whisper_model(model_path):
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model_path,
    )

    return pipe


# =========================================================
# SESSION STATE
# =========================================================

if "history" not in st.session_state:
    st.session_state.history = []


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ تنظیمات")


# -------------------------
# Whisper Model
# -------------------------

st.sidebar.subheader("🎙️ تنظیمات تبدیل گفتار")


# -------------------------
# Microphone
# -------------------------

st.sidebar.subheader("🎤 میکروفون")

try:

    devices = sd.query_devices()

    input_devices = [
        (i, device["name"])
        for i, device in enumerate(devices)
        if device["max_input_channels"] > 0
    ]

    if input_devices:

        device_labels = [
            f"{i} - {name}"
            for i, name in input_devices
        ]

        selected_mic = st.sidebar.selectbox(
            "انتخاب میکروفون",
            device_labels,
            index=0,
        )

        selected_index = int(
            selected_mic.split(" - ")[0]
        )

    else:

        st.sidebar.warning(
            "هیچ میکروفونی پیدا نشد."
        )

        selected_index = None

except Exception as e:

    st.sidebar.warning(
        "امکان شناسایی میکروفون وجود ندارد."
    )

    selected_index = None


# -------------------------
# TTS Settings
# -------------------------

st.sidebar.subheader("🔊 تنظیمات صدا")

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


# =========================================================
# MAIN TITLE
# =========================================================

st.title("🎙️ Speech & Voice AI")

st.caption(
    "تبدیل گفتار به متن و متن به گفتار"
)


# =========================================================
# TABS
# =========================================================

tab_stt, tab_tts = st.tabs(
    [
        "🎙️ گفتار → متن",
        "🔊 متن → گفتار",
    ]
)


# =========================================================
# SPEECH TO TEXT
# =========================================================

with tab_stt:

    st.header("🎙️ تبدیل گفتار به متن")

    st.write(
        "می‌توانید یک فایل صوتی آپلود کنید "
        "یا مستقیماً با میکروفون صحبت کنید."
    )


    # =====================================================
    # INPUT METHOD
    # =====================================================

    input_method = st.radio(
        "روش ورود صدا",
        [
            "📁 آپلود فایل صوتی",
            "🎤 ضبط با میکروفون",
        ],
        horizontal=True,
    )


    # =====================================================
    # UPLOAD AUDIO
    # =====================================================

    if input_method == "📁 آپلود فایل صوتی":

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
                "🚀 تبدیل فایل به متن",
                key="upload_to_text",
            ):

                progress = st.progress(
                    0,
                    text="0% - شروع پردازش",
                )

                try:

                    progress.progress(
                        20,
                        text="20% - در حال بارگذاری مدل",
                    )

                    pipe = pipeline(
                        "automatic-speech-recognition",
                        model=WHISPER_MODEL,
                    )

                    progress.progress(
                        60,
                        text="60% - مدل آماده پردازش",
                    )

                    audio_bytes = audio_file.read()

                    result = pipe(
                        audio_bytes,
                        return_timestamps=True,
                        generate_kwargs={
                            "language": "fa"
                        },
                    )

                    text = result["text"]

                    progress.progress(
                        100,
                        text="100% - پردازش کامل شد",
                    )

                    st.success(
                        "تبدیل با موفقیت انجام شد."
                    )

                    st.text_area(
                        "📝 متن استخراج شده",
                        text,
                        height=300,
                        key="uploaded_result",
                    )

                    st.session_state.history.append(
                        {
                            "type": "Speech → Text",
                            "text": text,
                            "model": model_name,
                        }
                    )

                except Exception as e:

                    st.error(
                        f"خطا در پردازش فایل:\n{e}"
                    )


    # =====================================================
    # MICROPHONE
    # =====================================================

    else:

        st.info(
            "برای شروع ضبط، روی دکمه میکروفون کلیک کنید."
        )

        audio = audio_recorder(
            "",
            pause_threshold=3.0,
        )

        if audio:

            st.audio(
                audio,
                format="audio/wav",
            )

            if st.button(
                "🚀 تبدیل صدای ضبط‌شده به متن",
                key="microphone_to_text",
            ):

                progress = st.progress(
                    0,
                    text="0% - شروع پردازش",
                )

                try:

                    progress.progress(
                        20,
                        text="20% - در حال بارگذاری مدل",
                    )

                    pipe = load_whisper_model(
                        MODELS[model_name]
                    )

                    progress.progress(
                        60,
                        text="60% - در حال تبدیل صدا",
                    )

                    result = pipe(
                        audio,
                        return_timestamps=True,
                        generate_kwargs={
                            "language": "fa"
                        },
                    )

                    text = result["text"]

                    progress.progress(
                        100,
                        text="100% - پردازش کامل شد",
                    )

                    st.success(
                        "صدای شما با موفقیت به متن تبدیل شد."
                    )

                    st.text_area(
                        "📝 متن استخراج شده",
                        text,
                        height=300,
                        key="microphone_result",
                    )

                    st.session_state.history.append(
                        {
                            "type": "Microphone → Text",
                            "text": text,
                            "model": model_name,
                        }
                    )

                except Exception as e:

                    st.error(
                        f"خطا در پردازش میکروفون:\n{e}"
                    )


# =========================================================
# TEXT TO SPEECH
# =========================================================

with tab_tts:

    st.header("🔊 تبدیل متن به گفتار")

    st.write(
        "متن خود را وارد کنید یا یک فایل TXT آپلود کنید."
    )


    # =====================================================
    # TEXT FILE
    # =====================================================

    text_file = st.file_uploader(
        "📄 فایل متنی",
        type=["txt"],
        key="tts_text_file",
    )


    # =====================================================
    # TEXT INPUT
    # =====================================================

    text_input = st.text_area(
        "⌨️ متن را وارد کنید",
        height=300,
        key="tts_text_input",
    )


    # =====================================================
    # GENERATE AUDIO
    # =====================================================

    if st.button(
        "🔊 تبدیل به ویس",
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
            text="0% - شروع",
        )


        try:

            progress.progress(
                30,
                text="30% - آماده‌سازی متن",
            )


            communicate = Communicate(
                text=text,
                voice=voice,
                rate=f"{rate:+d}%",
                volume=f"{volume:+d}%",
                pitch=f"{pitch:+d}Hz",
            )


            progress.progress(
                70,
                text="70% - در حال تولید صدا",
            )


            output_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp3",
            )

            output_path = output_file.name

            output_file.close()


            communicate.save_sync(
                output_path
            )


            progress.progress(
                100,
                text="100% - آماده شد",
            )


            st.success(
                "فایل صوتی با موفقیت ساخته شد."
            )


            st.audio(
                output_path,
                format="audio/mp3",
            )


            st.session_state.history.append(
                {
                    "type": "Text → Speech",
                    "text": text,
                    "voice": voice,
                }
            )


        except Exception as e:

            st.error(
                f"خطا در تبدیل متن به گفتار:\n{e}"
            )


# =========================================================
# HISTORY
# =========================================================

st.divider()

with st.expander("📜 تاریخچه پردازش‌ها"):

    if st.session_state.history:

        for index, item in enumerate(
            reversed(st.session_state.history),
            start=1,
        ):

            st.markdown(
                f"### {index}. {item['type']}"
            )

            if "model" in item:

                st.caption(
                    f"مدل: {item['model']}"
                )

            if "voice" in item:

                st.caption(
                    f"صدا: {item['voice']}"
                )

            st.write(
                item["text"]
            )

            st.divider()

    else:

        st.info(
            "هنوز پردازشی انجام نشده است."
        )
