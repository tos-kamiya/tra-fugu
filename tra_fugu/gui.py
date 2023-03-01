import argparse

from transformers import pipeline
import guietta
from guietta import Gui, _, ___, III, QPlainTextEdit, B, L
from qt_material import apply_stylesheet, list_themes

from .utils import paragraph_iter


DEFAULT_THEME = 'light_blue'


def main():
    parser = argparse.ArgumentParser(description='Tra-Fugu GUI, A GUI Translation app between English and Japanese')
    parser.add_argument('-d', '--device', type=int, default=-1, help='Run translation on a GPU of the ID (ID >= 0).')
    parser.add_argument('-t', '--theme', type=str, default=DEFAULT_THEME, help='Theme name. (default: %s)' % DEFAULT_THEME)
    parser.add_argument('--list-themes', action='store_true', help='Print theme names and exit.')

    args = parser.parse_args()

    if args.list_themes:
        print('Available themes:')
        for theme_name in list_themes():
            if theme_name.endswith('.xml'):
                theme_name = theme_name[:-len('.xml')]
            print('  ' + theme_name)
        return

    gpu_id = args.device
    qt_material_theme = args.theme + '.xml'

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
    original_text_box = ['']

    gui.translated.setStyleSheet("background-color: #b0b0b0")

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

    def original_text_changed(gui, *args):
        t = gui.original.toPlainText()
        is_changed = t.rstrip() != original_text_box[0].rstrip()
        if is_changed:
            gui.translated.setStyleSheet("background-color: #b0b0b0")
            original_text_box[0] = t

    gui.events(
        [ to_japanese, to_english, _, _, _, _ ],
        [ ('textChanged', original_text_changed), _, _, _, _, _],
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

    apply_stylesheet(guietta.app, theme=qt_material_theme)

    gui.run()


if __name__ == '__main__':
    main()
