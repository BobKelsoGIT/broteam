import os
import tempfile
from django.http import FileResponse
from django.shortcuts import render
from moviepy.editor import VideoFileClip
from .forms import VideoFileForm


def upload_video(request):
    if request.method == 'POST':
        form = VideoFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Сохраняем загруженное видео во временный файл
            video_file = form.cleaned_data['video']
            with tempfile.NamedTemporaryFile(delete=False,
                                             suffix='.mp4') as temp_video:
                for chunk in video_file.chunks():
                    temp_video.write(chunk)
                temp_video_path = temp_video.name

            # Извлечение аудио из видео
            audio_path = os.path.splitext(temp_video_path)[0] + '.mp3'
            try:
                video = VideoFileClip(temp_video_path)
                video.audio.write_audiofile(audio_path)
            finally:
                # Удаляем временный видеофайл
                os.remove(temp_video_path)

            # Отправляем аудиофайл как ответ
            try:
                response = FileResponse(open(audio_path, 'rb'),
                                        content_type='audio/mpeg')
                response[
                    'Content-Disposition'] = f'attachment; filename="{os.path.basename(audio_path)}"'
                return response
            finally:
                # Удаляем аудиофайл после отправки ответа
                os.remove(audio_path)
    else:
        form = VideoFileForm()

    return render(request, 'mediaextractor/upload.html', {'form': form})
