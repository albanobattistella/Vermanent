import gzip
import importlib.util
import json
import shutil
import tarfile
from tkinter import messagebox
import spacy
import subprocess
import sys
import mimetypes
import os
import zipfile
from pathlib import Path
import tempfile
import ctypes
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, Image

APP_TEMP_BASE = Path(tempfile.gettempdir()) / ".vermanent_temp"

ACCEPTED_AUDIO_MIME_TYPES = [
    "audio/mpeg", "audio/mp4", "audio/x-m4a", "audio/wav", "audio/x-wav",
    "audio/flac", "audio/aac", "audio/ogg", "audio/opus", "audio/x-ms-wma",
    "audio/x-aiff", "audio/amr", "audio/3gpp", "audio/webm", "audio/x-pn-wav",
    "audio/x-caf", "audio/x-matroska"
]


def is_valid_audio_filename(filename):
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type in ACCEPTED_AUDIO_MIME_TYPES


def is_supported_archive(path):
    ext = path.lower()
    return (
            zipfile.is_zipfile(path) or
            ext.endswith(('.tar', '.tar.gz', '.tgz', '.gz'))
    )


def genera_pdf_report(evidence_dict, results, output_path, logo_path=None, language={}):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=2 * cm, leftMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm)

    styles = getSampleStyleSheet()
    body_style = styles["BodyText"]
    body_style.spaceAfter = 6
    body_style.leading = 14

    story = []

    if logo_path and os.path.exists(logo_path):
        try:
            img = Image(logo_path, width=3*cm, height=3*cm)
            story.append(img)
            story.append(Spacer(1, 0.5*cm))
        except Exception as e:
            messagebox.showerror(message=f"Unexpected {e=}, {type(e)=}")

    story.append(Paragraph('<font color="#841818" size="25">'+language["report_title"]+'</font>', styles["Title"]))
    story.append(Spacer(1, 1*cm))

    story.append(Paragraph('<font color="#841818">'+language["general_data"]+'</font>', styles["Heading2"]))

    for key, value in evidence_dict.items():
        label = language.get(key, key.replace('_', ' ').capitalize())
        story.append(Paragraph(f"<b>{label}:</b> {value}", body_style))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"<b>{language['number_of_results']}</b> {len(results)}",
                           body_style))
    story.append(Spacer(1, 1*cm))

    for i, r in enumerate(results, 1):
        story.append(Paragraph(f"<b><font color='#841818'>{language['result']} {i}</font></b>", styles["Heading3"]))
        story.append(Spacer(1, 0.2*cm))

        for key in ["file_name", "evidence", "transcription", "language", "word_similarity",
                    "window_similarity", "average_similarity"]:
            label = language.get(key, key.replace('_', ' ').capitalize())
            val = r.get(key, "N/A")
            story.append(Paragraph(f"<b>{label}:</b> {val}", body_style))

        story.append(Spacer(1, 0.5*cm))

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"<font size=8 color=gray>{language['generated_on']} {now}</font>", styles["Normal"]))

    doc.build(story)


def extract_single_file_from_virtual_path(base_directory, virtual_path, is_temp_dir = True, extraction_temp_dir = None):
    if not base_directory or not virtual_path:
        return None
    if is_temp_dir:
        base_app_temp_dir = APP_TEMP_BASE
        os.makedirs(base_app_temp_dir, exist_ok=True)
        extraction_temp_dir = tempfile.TemporaryDirectory(dir=base_app_temp_dir)
        extraction_temp_dir_name = extraction_temp_dir.name
    else:
        os.makedirs(extraction_temp_dir, exist_ok=True)
        base_app_temp_dir = ""
        extraction_temp_dir_name = extraction_temp_dir

    path_segments = virtual_path.split('::')

    current_file_or_archive_path = os.path.join(base_directory, path_segments[0])
    extracted_file_path = None

    try:
        for i, segment in enumerate(path_segments):
            if i == 0:
                if not os.path.exists(current_file_or_archive_path):
                    print(f"Errore: File o archivio iniziale non trovato: {current_file_or_archive_path}")
                    return None
                if len(path_segments) == 1:
                    if current_file_or_archive_path.endswith('.gz'):
                        try:
                            with gzip.open(current_file_or_archive_path, 'rb') as gz_in:
                                output_file_name = os.path.basename(current_file_or_archive_path).replace('.gz', '')
                                output_file_path = os.path.join(base_app_temp_dir,
                                                                extraction_temp_dir_name,
                                                                output_file_name)
                                with open(output_file_path, 'wb') as gz_out:
                                    shutil.copyfileobj(gz_in, gz_out)
                                extracted_file_path = output_file_path
                                break
                        except Exception as e:
                            print(f"Errore durante la decompressione del file GZ diretto: {e}")
                            return None
                    else:
                        final_file_name = os.path.basename(current_file_or_archive_path)
                        final_dest_path = os.path.join(base_app_temp_dir,
                                                       extraction_temp_dir_name,
                                                       final_file_name)
                        shutil.copy(current_file_or_archive_path, final_dest_path)
                        extracted_file_path = final_dest_path
                        break
                continue
            is_last_segment = (i == len(path_segments) - 1)
            if zipfile.is_zipfile(current_file_or_archive_path):
                with zipfile.ZipFile(current_file_or_archive_path, 'r') as zf:
                    if is_last_segment:
                        try:
                            zf.extract(segment, path=os.path.join(base_app_temp_dir, extraction_temp_dir_name))
                            extracted_file_path = os.path.join(base_app_temp_dir, extraction_temp_dir_name, segment)
                            break
                        except KeyError as e:
                            messagebox.showerror(message=f"Unexpected {e=}, {type(e)=}")
                            return None
                    else:
                        nested_item_name = segment

                        if nested_item_name not in zf.namelist():
                            print(f"Errore: Elemento annidato '{nested_item_name}' non trovato nell'archivio ZIP.")
                            return None
                        zf.extract(nested_item_name, os.path.join(base_app_temp_dir, extraction_temp_dir_name))
                        current_file_or_archive_path = os.path.join(base_app_temp_dir, extraction_temp_dir_name, nested_item_name)

            elif tarfile.is_tarfile(current_file_or_archive_path):
                with tarfile.open(current_file_or_archive_path, 'r') as tf:
                    if is_last_segment:
                        try:
                            tf.extract(segment, path=os.path.join(base_app_temp_dir, extraction_temp_dir_name))
                            extracted_file_path = os.path.join(base_app_temp_dir, extraction_temp_dir_name, segment)
                            break
                        except KeyError as err:
                            messagebox.showerror(message=f"Unexpected {err=}, {type(err)=}")
                            return None
                        except Exception as e:
                            messagebox.showerror(message=f"Unexpected {e=}, {type(e)=}")
                            return None
                    else:
                        nested_item_name = segment
                        try:
                            tf.getmember(nested_item_name)
                        except KeyError as e:
                            messagebox.showerror(message=f"Unexpected {e=}, {type(e)=}")
                            return None

                        tf.extract(nested_item_name, path=os.path.join(base_app_temp_dir, extraction_temp_dir_name))
                        current_file_or_archive_path = os.path.join(base_app_temp_dir, extraction_temp_dir_name, nested_item_name)

            elif current_file_or_archive_path.endswith('.gz'):
                if is_last_segment:
                    try:
                        with gzip.open(current_file_or_archive_path, 'rb') as gz_in:
                            output_file_name = os.path.basename(segment)
                            output_file_path = os.path.join(base_app_temp_dir, extraction_temp_dir_name, output_file_name)
                            with open(output_file_path, 'wb') as gz_out:
                                shutil.copyfileobj(gz_in, gz_out)
                            extracted_file_path = output_file_path
                            break
                    except Exception as e:
                        messagebox.showerror(message=f"Unexpected {e=}, {type(e)=}")
                        return None
                else:
                    print(
                        f"Errore: Un file GZ ('{current_file_or_archive_path}') non può contenere altri archivi o percorsi annidati dopo '::'.")
                    return None
            else:
                print(f"Formato archivio non supportato o elemento non valido: {current_file_or_archive_path}")
                return None

    except Exception as e:
        messagebox.showerror(message=f"Unexpected {e=}, {type(e)=}")
        if os.path.exists(os.path.join(base_app_temp_dir, extraction_temp_dir_name)):
            shutil.rmtree(os.path.join(base_app_temp_dir, extraction_temp_dir_name))
        return None
    if extracted_file_path is None:
        print(f"Attenzione: Il file '{virtual_path}' non è stato trovato o estratto.")
        if os.path.exists(os.path.join(base_app_temp_dir, extraction_temp_dir_name)):
            shutil.rmtree(os.path.join(base_app_temp_dir, extraction_temp_dir_name))
        return None

    return extracted_file_path, extraction_temp_dir


def extract_to_temp(path):
    temp_dir = tempfile.TemporaryDirectory(dir=APP_TEMP_BASE)
    lower = path.lower()

    try:

        if zipfile.is_zipfile(path):
            with zipfile.ZipFile(path, 'r') as zf:
                zf.extractall(path=temp_dir.name)

        elif lower.endswith(('.tar', '.tar.gz', '.tgz')):
            with tarfile.open(path, 'r:*') as tf:
                tf.extractall(path=temp_dir.name)

        elif lower.endswith('.gz') and not lower.endswith('.tar.gz'):
            with gzip.open(path, 'rb') as gz_in:
                out_name = os.path.splitext(os.path.basename(path))[0]
                out_path = os.path.join(temp_dir.name, out_name)
                with open(out_path, 'wb') as f_out:
                    shutil.copyfileobj(gz_in, f_out)

        return temp_dir.name, temp_dir
    except Exception:
        temp_dir.cleanup()
        return None, None


def extract_to_file_to_temp(path):
    temp_dir = tempfile.TemporaryDirectory(dir=APP_TEMP_BASE)
    lower = path.lower()

    try:

        if zipfile.is_zipfile(path):
            with zipfile.ZipFile(path, 'r') as zf:
                zf.extractall(path=temp_dir.name)

        elif lower.endswith(('.tar', '.tar.gz', '.tgz')):
            with tarfile.open(path, 'r:*') as tf:
                tf.extractall(path=temp_dir.name)

        elif lower.endswith('.gz') and not lower.endswith('.tar.gz'):
            with gzip.open(path, 'rb') as gz_in:
                out_name = os.path.splitext(os.path.basename(path))[0]
                out_path = os.path.join(temp_dir.name, out_name)
                with open(out_path, 'wb') as f_out:
                    shutil.copyfileobj(gz_in, f_out)

        return temp_dir.name, temp_dir
    except Exception:
        temp_dir.cleanup()
        return None, None


def scan_for_virtual_audio_paths(root_path):
    virtual_paths = []

    def recursive_scan(current_path, virtual_prefix=""):
        for entry in os.scandir(current_path):
            full_path = os.path.join(current_path, entry.name)
            virt_path = f"{virtual_prefix}{entry.name}" if virtual_prefix else entry.name

            if entry.is_dir():
                recursive_scan(full_path, virt_path + "/")

            elif entry.is_file():
                if is_valid_audio_filename(entry.name):
                    virtual_paths.append(virt_path)

                elif is_supported_archive(full_path):
                    extracted_path, temp_dir = extract_to_temp(full_path)
                    if extracted_path:
                        recursive_scan(extracted_path, virt_path + "::")
                        temp_dir.cleanup()

    recursive_scan(root_path)
    return virtual_paths


def load_audio_from_virtual_path(virtual_path, input_root):
    if "::" not in virtual_path:
        abs_path = os.path.join(input_root, virtual_path)
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"File non trovato: {abs_path}")
        return abs_path, None

    return extract_single_file_from_virtual_path(input_root, virtual_path)


def hide_windows_dir(path):
    if os.name == "nt":
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ctypes.windll.kernel32.SetFileAttributesW(str(path), FILE_ATTRIBUTE_HIDDEN)


def cleanup_temp_dir():
    try:
        APP_TEMP_BASE.mkdir(parents=True, exist_ok=True)
        hide_windows_dir(APP_TEMP_BASE)

        for item in APP_TEMP_BASE.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
            except Exception as e:
                messagebox.showwarning(message=f"Unexpected {e=}, {type(e)=}")
    except Exception as e:
        messagebox.showerror(message=f"Unexpected {e=}, {type(e)=}")


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def check_dependencies():
    if shutil.which("ffmpeg") is None:
        messagebox.showerror("Dependence not found", "ffmpeg not found")
        return False
    dependencies = ['whisper', 'PIL', 'customtkinter', 'reportlab', 'stanza', 'torch', 'spacy']
    for dependence in dependencies:
        if importlib.util.find_spec(dependence) is None:
            messagebox.showerror("Dependence not found", f"{dependence} not found")
            return False
    with open("search/languages.json") as languages_file:
        languages = json.load(languages_file)
        info = spacy.info()
        models = info["pipelines"]
        installed_models = []
        for model in models:
            installed_models.append(model)
        for language in languages:
            if languages[language]["model"] not in installed_models and languages[language]["spacy"] is True:
                messagebox.showerror("Model not found", f"{languages[language]['model']} not found")
                return False
    return True
