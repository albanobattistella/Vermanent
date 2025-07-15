import json
import spacy
from threading import Thread
from search.SearchSyncData import SearchSyncData
import stanza
from spacy import load, Language
from stanza import DownloadMethod
from search.stopwords.it_stopwords import it_stopwords


class Preprocessor(Thread,):

    def __init__(self,
                 case_name: str,
                 evidence: str,
                 sync_data: SearchSyncData,
                 searched_text: str,
                 searched_text_lang: str,
                 db):
        self.searched_text_lang = searched_text_lang
        self._nlp = dict()
        with open("search/languages.json", "r") as file:
            languages = json.load(file)
        self.languages = languages
        Thread.__init__(self)
        self.evidence = evidence
        self.case_name = case_name
        self.sync_data = sync_data
        self.db_interface = db
        self.searched_text = searched_text

    @staticmethod
    def stop_word_removal(text: str,
                          nlp):
        text = text.lower()
        text = text.replace("'", "' ").replace(",", "").split()

        text = [word for word in text if word not in nlp.Defaults.stop_words]
        return " ".join(text)

    @staticmethod
    def transform_into_lemma(text: str,
                             nlp):
        doc = nlp(text)
        text = []
        for token in doc:
            text.append(token.lemma_)
        text = " ".join(text)
        return text

    def load_model(self,
                   language):
        try:
            nlp = self._nlp[language]
        except KeyError:
            model = self.languages[language]

            if not model["spacy"]:
                stanza_nlp = stanza.Pipeline(lang=language,
                                             processors='tokenize,pos,lemma',
                                             download_method=DownloadMethod.REUSE_RESOURCES,
                                             verbose=False,
                                             use_gpu=False)

                @Language.component("stanza_lemmatizer")
                def stanza_lemmatizer(doc):
                    doc_stanza = stanza_nlp(doc.text)
                    stanza_tokens = []
                    for sent in doc_stanza.sentences:
                        stanza_tokens.extend(sent.words)

                    if len(doc) != len(stanza_tokens):
                        print("Warning: token count mismatch")

                    for token_spacy, token_stanza in zip(doc, stanza_tokens):
                        token_spacy.lemma_ = token_stanza.lemma
                        token_spacy.pos_ = token_stanza.upos
                    return doc

                nlp = spacy.load(model["model"])
                stopwords = it_stopwords
                nlp.Defaults.stop_words = it_stopwords
                for w in stopwords:
                    nlp.vocab[w].is_stop = True
                nlp.add_pipe("stanza_lemmatizer", last=True)
            else:
                nlp = load(model["model"])
            self._nlp.update({language: nlp})
        return nlp

    def prepare_for_search(self,
                           text: str,
                           language: str):
        try:
            nlp = self.load_model(language=language)
            text = self.stop_word_removal(text=text,
                                          nlp=nlp)
            text = self.transform_into_lemma(text=text,
                                             nlp=nlp)
            return nlp(text)
        except KeyError:
            return None

    def run(self):
        self.db_interface.remove_current_search(case_name=self.case_name,
                                                evidence=self.evidence)

        data = self.db_interface.take_transcribed_text(case_name=self.case_name,
                                                       evidence=self.evidence)
        print(data)

        for d in data:
            self.db_interface.insert_file_id_and_evidence(case_name=self.case_name,
                                                          evidence=self.evidence,
                                                          file_id=d["id"])
        nlp_searched_text = self.prepare_for_search(text=self.searched_text,
                                                    language=self.searched_text_lang)
        for d in data:
            self.sync_data.put_on_to_analyze_queue({
                "id": d["id"],
                "nlp": self.prepare_for_search(text=d["text"],
                                               language=d["language"]),
                "nlp_searched_text": nlp_searched_text,
                "language": d["language"]
            })
        self.sync_data.put_on_to_analyze_queue(None)
        self._nlp.clear()



