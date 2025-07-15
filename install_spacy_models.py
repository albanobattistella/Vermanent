import json
import subprocess
import sys
import spacy

with open("search/languages.json") as languages_file:
    languages = json.load(languages_file)
    info = spacy.info()
    models = info["pipelines"]
    installed_models = []
    for model in models:
        installed_models.append(model)
    for language in languages:
        if languages[language]["model"] not in installed_models and languages[language]["spacy"] is True:
            subprocess.check_call([sys.executable, "-m", "spacy", "download", languages[language]["model"]])
