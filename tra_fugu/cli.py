import argparse
import os.path
import sys

from transformers import pipeline

from .utils import paragraph_iter


def main():
    parser = argparse.ArgumentParser(description='Translate English text into Japanese or vice versa.')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', action='store_true', help='Translate into English text.')
    group.add_argument('-j', action='store_true', help='Translate into Japanese text.')

    parser.add_argument('-s', action='store_true', help="For each input file, save the translation result is saved with the file name adding '-jpn' or '-eng' as suffix.")
    parser.add_argument('-d', '--device', type=int, default=-1, help='Run translation on a GPU of the ID (ID >= 0).')

    parser.add_argument('textfile', nargs='*', help='Input text file(s).')

    args = parser.parse_args()

    if args.e:
        translation_type = 'eng'
    else:
        translation_type = 'jpn'

    input_files = args.textfile
    save_output = args.s
    gpu_id = args.device

    if save_output:
        if not input_files:
            sys.exit('Error: no input file specified.')
        if '-' in input_files:
            sys.exit('Error: option -s can not be specified along with the standard input.')
    if not input_files:
        input_files = ['-']
    for f in input_files:
        if f == '-':
            continue  # for f
        if not (os.path.exists(f) and os.path.isfile(f)):
            sys.exit('Error: file does not exist: %s' % f)

    suffix = '-' + translation_type
    if translation_type == 'eng':
        translator = pipeline("translation", model="staka/fugumt-ja-en", device=gpu_id)
    else:
        suffix = '-jpn'
        translator = pipeline("translation", model="staka/fugumt-en-ja", device=gpu_id)

    if gpu_id < 0:  # model is running on cpu
        def translate_paragraphs(paragraph_it):
            result_texts = []
            for paragraph in paragraph_it:
                result = translator('\n'.join(paragraph))
                result_texts.append(result[0]['translation_text'])
            return result_texts
    else:
        def translate_paragraphs(paragraph_it):
            paragraph_texts = list('\n'.join(p) for p in paragraph_it)
            result_texts = [r['translation_text'] for r in translator(paragraph_texts)]
            return result_texts

    for fi, f in enumerate(input_files):
        if not save_output and fi > 0:
            print('---')

        if f == '-':
            text = sys.stdin.read()
        else:
            with open(f) as inp:
                text = inp.read()

        if save_output:
            fn, ext = os.path.splitext(f)
            output_file = fn + suffix + ext
            with open(output_file, 'w') as outp:
                for ti, t in enumerate(translate_paragraphs(paragraph_iter(text))):
                    if ti > 0:
                        print(file=outp)
                    print(t, file=outp)
        else:
            for ti, t in enumerate(translate_paragraphs(paragraph_iter(text))):
                if ti > 0:
                    print()
                print(t)


if __name__ == '__main__':
    main()
