import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display

from pages._i18n import t


def render():
    """Affiche la page d'analyse audio d'un enregistrement d'oiseau.

    Permet à l'utilisateur d'importer un fichier audio (MP3, WAV, OGG, FLAC)
    et génère trois représentations visuelles :

    - **Forme d'onde** : amplitude du signal en fonction du temps.
    - **Spectrogramme Mel** : énergie fréquentielle sur une échelle Mel (dB),
      adapté à la perception auditive.
    - **Spectrogramme log-fréquentiel** : STFT avec axe des fréquences
      logarithmique (dB), utile pour visualiser les harmoniques.

    Affiche également des métriques techniques (fréquence d'échantillonnage,
    durée, nombre d'échantillons) et un lecteur audio intégré.
    """
    st.header(t("audio.header"))

    # Widget d'import de fichier audio (formats courants pris en charge)
    audio_file = st.file_uploader(
        t("audio.uploader"),
        type=["mp3", "wav", "ogg", "flac"],
        key="audio_uploader",
    )

    # Aucun fichier sélectionné : affiche un message d'aide et sort
    if audio_file is None:
        st.info(t("audio.empty"))
        return

    # Détermine le type MIME pour le lecteur audio HTML5
    file_name = audio_file.name.lower()
    if file_name.endswith(".mp3"):
        mime_type = "audio/mpeg"
    elif file_name.endswith(".wav"):
        mime_type = "audio/wav"
    elif file_name.endswith(".ogg"):
        mime_type = "audio/ogg"
    else:
        mime_type = "audio/*"

    # Lecteur audio natif Streamlit
    st.subheader(t("audio.player.header"))
    st.audio(audio_file, format=mime_type)

    # Chargement et analyse du fichier avec librosa (peut être lent pour les gros fichiers)
    with st.spinner(t("audio.loading")):
        try:
            # sr=None conserve la fréquence d'échantillonnage originale du fichier
            y, sr = librosa.load(audio_file, sr=None, mono=True)
            duration = len(y) / sr if sr else 0

            # Métriques techniques du fichier audio
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(t("audio.metric.sr"), f"{sr:,} Hz")
            with col2:
                st.metric(t("audio.metric.duration"), f"{duration:.2f} s")
            with col3:
                st.metric(t("audio.metric.samples"), f"{len(y):,}")

            # --- Forme d'onde temporelle ---
            st.divider()
            st.subheader(t("audio.waveform.header"))
            fig_wave, ax_wave = plt.subplots(figsize=(12, 3))
            librosa.display.waveshow(y, sr=sr, ax=ax_wave)
            ax_wave.set_title(t("audio.waveform.title"))
            ax_wave.set_xlabel(t("audio.waveform.x"))
            ax_wave.set_ylabel(t("audio.waveform.y"))
            fig_wave.tight_layout()
            st.pyplot(fig_wave)
            plt.close(fig_wave)  # Libère la mémoire matplotlib

            # --- Spectrogramme Mel ---
            st.divider()
            st.subheader(t("audio.mel.header"))
            mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
            # Conversion en dB avec référence au max pour un meilleur contraste visuel
            mel_db = librosa.power_to_db(mel, ref=np.max)
            fig_mel, ax_mel = plt.subplots(figsize=(12, 4))
            img_mel = librosa.display.specshow(mel_db, sr=sr, x_axis="time", y_axis="mel", ax=ax_mel, cmap="magma")
            ax_mel.set_title(t("audio.mel.title"))
            ax_mel.set_xlabel(t("audio.mel.x"))
            ax_mel.set_ylabel(t("audio.mel.y"))
            fig_mel.colorbar(img_mel, ax=ax_mel, format="%+2.0f dB")
            fig_mel.tight_layout()
            st.pyplot(fig_mel)
            plt.close(fig_mel)

            # --- Spectrogramme log-fréquentiel (STFT) ---
            st.divider()
            st.subheader(t("audio.log.header"))
            stft = librosa.stft(y)
            # Amplitude → dB avec référence au max
            spec_db = librosa.amplitude_to_db(np.abs(stft), ref=np.max)
            fig_spec, ax_spec = plt.subplots(figsize=(12, 4))
            img_spec = librosa.display.specshow(spec_db, sr=sr, x_axis="time", y_axis="log", ax=ax_spec, cmap="magma")
            ax_spec.set_title(t("audio.log.title"))
            ax_spec.set_xlabel(t("audio.log.x"))
            ax_spec.set_ylabel(t("audio.log.y"))
            fig_spec.colorbar(img_spec, ax=ax_spec, format="%+2.0f dB")
            fig_spec.tight_layout()
            st.pyplot(fig_spec)
            plt.close(fig_spec)

        except Exception as e:
            # Fichier corrompu ou format non supporté par librosa
            st.error(t("audio.error", e=e))
