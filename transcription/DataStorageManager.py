from threading import Thread
from db.DbInterface import DbInterface
from transcription.TranscriptionSyncData import TranscriptionSyncData


class DataStorageManager(Thread):

    def __init__(self,
                 transcription_sync_data: TranscriptionSyncData):
        Thread.__init__(self)
        self.db_interface = DbInterface()
        self.transcription_sync_data = transcription_sync_data

    def run(self):
        data = self.transcription_sync_data.get_from_queue()
        while data is not None:
            self.db_interface.insert_transcription(self.transcription_sync_data.get_case_name(),
                                                   self.transcription_sync_data.get_evidence(),
                                                   data)
            data = self.transcription_sync_data.get_from_queue()
        return
