import whisper
from utils import load_audio_from_virtual_path
from threading import Thread
from transcription.TranscriptionSyncData import TranscriptionSyncData
from gui.Observer.Subject import Subject


class Transcriber(Thread, Subject):

    def __init__(self, transcription_sync_data: TranscriptionSyncData,
                 transcriptions_language,
                 model,
                 semaphore):
        Thread.__init__(self)
        self._finalization_done_observers = []
        self.transcriptions_language = transcriptions_language
        self.stop_process = False
        self._model = model["model"]
        self.mode = model["mode"]
        self.mutex = semaphore
        self.transcription_sync_data = transcription_sync_data
        self.chunk_seconds = model["chunk_seconds"]

    def select_language(self,
                        audio):
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio, n_mels=128).to(self._model.device)
        if self.transcriptions_language == "Multilanguage":
            _, probs = self._model.detect_language(mel)
            language = max(probs, key=probs.get)
        else:
            language = self.transcriptions_language
        return language

    def transcribe(self, file):
        audio = whisper.load_audio(file)
        audio = whisper.pad_or_trim(audio)
        total_samples = len(audio)
        language = self.select_language(audio=audio)
        options = whisper.DecodingOptions(language=language, fp16=False)

        text = ""
        for start in range(0, total_samples, self.chunk_seconds * 16000):
            if self.mode == "GPU":  # Used to have single access on the whisper model, but to have concurrency with CPU
                self.mutex.acquire()
            if self.stop_process:
                self.mutex.release()
                return None, language
            end = min(start + self.chunk_seconds * 16000, total_samples)
            chunk = audio[start:end]
            chunk = whisper.pad_or_trim(chunk)
            mel = whisper.log_mel_spectrogram(chunk, n_mels=128).to(self._model.device)
            result = whisper.decode(self._model, mel, options)
            text += result.text + " "
            if self.mode == "GPU":
                self.mutex.release()
        return text.strip(), language

    def stop(self):
        self.stop_process = True

    def run(self):
        if self._model is None:
            self._model = whisper.load_model("large")
        file = self.transcription_sync_data.get_file()

        while file is not None:
            path, temp_dir = load_audio_from_virtual_path(file[1], file[0])
            text, language = self.transcribe(path)
            if temp_dir is not None:
                temp_dir.cleanup()
            if text is None:
                self.transcription_sync_data.put_on_queue(None)
                self.notify()
                break
            self.transcription_sync_data.put_on_queue([file[1], text, language])
            file = self.transcription_sync_data.get_file()
        return

    def attach(self, observer) -> None:
        self._finalization_done_observers.append(observer)

    def detach(self, observer) -> None:
        self._finalization_done_observers.remove(observer)

    def notify(self) -> None:
        for observer in self._finalization_done_observers:
            observer.update(self)
