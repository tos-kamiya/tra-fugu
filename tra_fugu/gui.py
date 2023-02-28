import argparse

from guietta import Gui, _, ___, III, QPlainTextEdit, B, L
from transformers import pipeline

from .utils import paragraph_iter


def main():
    parser = argparse.ArgumentParser(description='Tra-Fugu GUI, A GUI Translation app between English and Japanese')
    parser.add_argument('-d', '--device', type=int, default=-1, help='Run translation on a GPU of the ID (ID >= 0).')
    args = parser.parse_args()
    gpu_id = args.device

    ej_translator = None
    je_translator = None

    TE = QPlainTextEdit

    device_label = 'device: ' + ('GPU' if gpu_id >= 0 else 'CPU')

    gui = Gui(
        [ (B('\u279c Japanese'), 'toj'), (B('\u279c English'), 'toe'), _, _, _, _ ],
        [ (TE, 'original'), ___, ___, (TE, 'translated'), ___, ___ ],
        [ III,              III, III, III,                III, III ],
        [ III,              III, III, III,                III, III ],
        [ '__status__', ___, ___, ___, ___, (L(device_label), 'devlabel') ],
    )
    def buttons_set_enabled(gui, enabled, status_message):
        gui.toj.setEnabled(enabled)
        gui.toe.setEnabled(enabled)
        gui.status = status_message

    gui.title("Translator by FuguMT (GUI)")

    o = gui.original
    o.setFocus()
    o.setStyleSheet("background-color: #FFFFFF")
    o.setPlaceholderText('Put the text you want to translate.')

    gui.translated.setStyleSheet("background-color: #A0A0A0")

    def translate_task(text, translator):
        assert translator is not None
        if translator.device.type == 'cpu':
            result_texts = []
            for paragraph in paragraph_iter(text):
                result = translator('\n'.join(paragraph))
                result_texts.append(result[0]['translation_text'])
        else:
            paragraph_texts = list('\n'.join(p) for p in paragraph_iter(text))
            result_texts = [r['translation_text'] for r in translator(paragraph_texts)]
        return (result_texts,)

    def translation_done_callback(gui, result_texts):
        gui.translated.setStyleSheet("background-color: #FFFFFF")
        gui.translated.setPlainText('\n\n'.join(result_texts))
        buttons_set_enabled(gui, True, '[Info] Ready.')

    def to_japanese(gui, *args):
        buttons_set_enabled(gui, False, '[Info] Translating into Japanese...')
        gui.execute_in_background(
            translate_task,
            args=(gui.original.toPlainText(), ej_translator),
            callback=translation_done_callback
        )

    def to_english(gui, *args):
        buttons_set_enabled(gui, False, '[Info] Translating into English...')
        gui.execute_in_background(
            translate_task,
            args=(gui.original.toPlainText(), je_translator),
            callback=translation_done_callback
        )

    gui.events(
        [ to_japanese, to_english, _, _, _, _ ],
        [ _, _, _, _, _, _],
        [ _, _, _, _, _, _],
        [ _, _, _, _, _, _],
    )

    def load_model():
        nonlocal ej_translator, je_translator
        ej_translator = pipeline("translation", model="staka/fugumt-en-ja", device=gpu_id)
        je_translator = pipeline("translation", model="staka/fugumt-ja-en", device=gpu_id)
    def load_model_done(gui, *args):
        buttons_set_enabled(gui, True, '[Info] Ready.')

    buttons_set_enabled(gui, False, '[Info] Loading translation models...')
    gui.execute_in_background(load_model, callback=load_model_done)

    gui.run()


if __name__ == '__main__':
    main()
