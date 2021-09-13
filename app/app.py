import streamlit as st
import soundfile as sf
from pedalboard import (
    Pedalboard,
    Chorus,
    Compressor,
    Convolution,
    Distortion,
    Gain,
    HighpassFilter,
    LadderFilter,
    Limiter,
    LowpassFilter,
    NoiseGate,
    Phaser,
    Reverb,
)


objects_and_init_kwargs = [
    (
        Chorus,
        {
            "rate_hz": 1.0,
            "depth": 0.25,
            "centre_delay_ms": 7.0,
            "feedback": 0.0,
            "mix": 0.5,
        },
    ),
    (Compressor, {"threshold_db": 0, "ratio": 1, "attack_ms": 1.0, "release_ms": 100}),
    # TODO - maybe add a few impulse responses to a folder + let folks cycle through them.
    # (Convolution, {'impulse_response_filename': None, 'mix': 1.0}),
    (Distortion, {"drive_db": 25}),
    (Gain, {"gain_db": 1.0}),
    (HighpassFilter, {"cutoff_frequency_hz": 50}),
    (LadderFilter, {"mode": LadderFilter.LPF12, "cutoff_hz": 200, "drive": 1.0}),
    (Limiter, {"threshold_db": -10.0, "release_ms": 100.0}),
    (LowpassFilter, {"cutoff_frequency_hz": 50}),
    (
        NoiseGate,
        {"threshold_db": -100.0, "ratio": 10, "attack_ms": 1.0, "release_ms": 100.0},
    ),
    (
        Phaser,
        {
            "rate_hz": 1.0,
            "depth": 0.5,
            "centre_frequency_hz": 1300.0,
            "feedback": 0.0,
            "mix": 0.5,
        },
    ),
    (
        Reverb,
        {
            "room_size": 0.5,
            "damping": 0.5,
            "wet_level": 0.33,
            "dry_level": 0.4,
            "width": 1.0,
            "freeze_mode": 0.0,
        },
    ),
]

name_to_object_init_kwargs = {
    obj.__name__: (obj, kwargs) for obj, kwargs in objects_and_init_kwargs
}


def get_transform_names(augmentations):
    transform_names = [st.sidebar.selectbox("Select transformation №1:", augmentations)]
    while transform_names[-1] != "None":
        transform_names.append(
            st.sidebar.selectbox(
                f"Select transformation №{len(transform_names) + 1}:",
                ["None"] + augmentations,
            )
        )
    transform_names = transform_names[:-1]
    return transform_names


def get_transforms():
    transform_names = get_transform_names(sorted(name_to_object_init_kwargs.keys()))

    transforms = []
    for i, name in enumerate(transform_names):
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"#### transformation №{i + 1}: {name}")
        obj, kwargs = name_to_object_init_kwargs[name]

        # 🚨 OMG pls no 🤮. It doesn't have to be this way. Do anything but this. 🚨
        inputs = {}
        for k, v in kwargs.items():
            if k in ["mix", "room_size", "damping", "wet_level", "dry_level", "width", "freeze_mode", 'feedback']:
                x = st.sidebar.slider(k, 0.0, 1.0, 0.1, key=f"{k}_{i}")
            elif k in ['threshold_db', 'gain_db']:
                x = st.sidebar.slider(k, -20., 20., 0., key=f"{k}_{i}")
            elif k in ['rate_hz', 'centre_delay_ms', 'depth']:
                x = st.sidebar.slider(k, 0., 10., 0.5, key=f"{k}_{i}")
            elif k in ['drive_db']:
                x = st.sidebar.slider(k, 0., 20., 0., key=f"{k}_{i}")
            elif k in ['release']:
                x = st.sidebar.slider(k, 0.01, 5000., 100., key=f"{k}_{i}")
            elif k in ['ratio', 'drive']:
                x = st.sidebar.slider(k, 1.0, 20., 4., key=f"{k}_{i}")
            elif k in ['attack_ms', 'release_ms']:
                x = st.sidebar.slider(k, 0.1, 2000., key=f"{k}_{i}")
            elif k in ['cutoff_frequency_hz', 'cutoff_hz', 'centre_frequency_hz']:
                x = st.sidebar.slider(k, 20, 20000, key=f"{k}_{i}")
            elif k in ['mode']:
                choices = [LadderFilter.LPF12, LadderFilter.HPF12, LadderFilter.BPF12, LadderFilter.LPF24, LadderFilter.HPF24, LadderFilter.BPF24]
                x = st.sidebar.selectbox(k, choices)
            else:
                x = type(v)(st.sidebar.text_input(k, value=v))
            inputs[k] = x
        
        # st.json(inputs)
        transforms.append(obj(**inputs))
    return transforms


# 🚨 TODO - messy. clean me pls.

audio_file = open('./download.wav', 'rb')
audio_bytes = audio_file.read()

st.markdown("## Input Audio")
st.audio(audio_bytes, format='audio/ogg')

# Run the audio through this pedalboard!
audio, sample_rate = sf.read('./download.wav')
board = Pedalboard(get_transforms(), sample_rate=sample_rate)
effected = board(audio)

# Write the audio back as a wav file:
with sf.SoundFile('./outputs.wav', 'w', samplerate=sample_rate, channels=len(effected.shape)) as f:
    f.write(effected)


audio_file = open('./outputs.wav', 'rb')
audio_bytes = audio_file.read()

st.markdown("## Effected Audio")
st.audio(audio_bytes, format='audio/wav')


from matplotlib import pyplot as plt
import librosa
import librosa.display

fig = plt.figure(figsize=(14, 5))
librosa.display.waveplot(effected, sr=sample_rate)
st.pyplot(fig)
