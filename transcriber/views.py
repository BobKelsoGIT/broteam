import os
from django.shortcuts import render
from django.core.files.storage import default_storage
from .forms import MediaFileForm
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from vosk import Model, KaldiRecognizer
import json
import wave
from asgiref.sync import sync_to_async

# Путь к модели Vosk
MODEL_PATH = "transcriber/models/us"


def process_media_file(media_file):
    """
    Обрабатывает медиафайл. Если это видеофайл, извлекает аудио и сохраняет его в формате WAV.
    Если это аудиофайл в формате, отличном от WAV, конвертирует его в WAV.
    Конвертирует аудиофайл в моно канал, 16000 Гц частоту дискретизации и 16 бит динамический диапазон.

    :param media_file: Путь к исходному медиафайлу.
    :return: Путь к обработанному аудиофайлу в формате WAV.
    """
    # Определяем формат видеофайла
    if media_file.endswith(('.mp4', '.avi', '.mov')):
        # Если это видеофайл, извлекаем аудио из видео
        video = VideoFileClip(media_file)
        audio_path = os.path.splitext(media_file)[0] + '.wav'
        video.audio.write_audiofile(audio_path)
    else:
        # Если это аудиофайл, проверяем его формат
        audio_path = media_file

    # Конвертируем файл в нужный формат, если он не в формате WAV
    if not audio_path.endswith('.wav'):
        audio = AudioSegment.from_file(audio_path)
        wav_path = os.path.splitext(audio_path)[0] + '.wav'
        audio.export(wav_path, format='wav')
        audio_path = wav_path

    # Открываем файл для конвертации в нужный формат
    audio = AudioSegment.from_wav(audio_path)

    # Конвертируем в моно канал, 16000 Гц частоту дискретизации и 16 бит
    audio = audio.set_channels(1)  # Устанавливаем моно канал
    audio = audio.set_frame_rate(16000)  # Устанавливаем частоту дискретизации
    audio = audio.set_sample_width(2)  # Устанавливаем 16 бит (2 байта) динамический диапазон

    # Сохраняем измененный файл
    final_path = os.path.splitext(audio_path)[0] + '_processed.wav'
    audio.export(final_path, format='wav')

    # Удаляем временный файл, если он был создан
    if audio_path != final_path and os.path.exists(audio_path):
        os.remove(audio_path)

    return final_path


def transcribe_audio(file_path, model_path):
    """
    Транскрибирует аудиофайл с использованием Vosk.

    :param file_path: Путь к аудиофайлу (должен быть в формате WAV).
    :param model_path: Путь к директории с моделью Vosk.
    :return: Текст транскрипции.
    """
    model = Model(model_path)
    wf = wave.open(file_path, "rb")

    if wf.getsampwidth() != 2:
        raise ValueError("Формат аудиофайла должен быть 16-бит PCM")
    if wf.getnchannels() != 1:
        raise ValueError("Аудиофайл должен быть моно")

    rec = KaldiRecognizer(model, wf.getframerate())
    transcription = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = rec.Result()
            transcription += json.loads(result).get('text', '') + ' '

    result = rec.FinalResult()
    transcription += json.loads(result).get('text', '')

    return transcription


async def upload_and_transcribe(request):
    transcription = None

    if request.method == 'POST':
        form = MediaFileForm(request.POST, request.FILES)
        if form.is_valid():
            media_instance = await sync_to_async(form.save)()
            media_file = media_instance.file.path
            audio_path = process_media_file(media_file)

            try:
                transcription = await sync_to_async(lambda: transcribe_audio(audio_path, MODEL_PATH))()
            finally:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                if os.path.exists(media_file):
                    default_storage.delete(media_file)

    else:
        form = MediaFileForm()

    return await sync_to_async(render)(request, 'components/upload.html', {
        'form': form,
        'transcription': transcription,
        'title': '',
        'button': 'Извлечь текст',
    })
