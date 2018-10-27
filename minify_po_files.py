"""Removes all unnecessary lines from .po files.

Created by William Hingston on 16/09/2018.

See:
    $ python minify_po_files.py -h
"""

import argparse
import os


def translate_po_files(lang: str, line: str):
    if "%(" not in line and "</" not in line and line is not "":
        # print( line)
        pass
    else:
        pass

    """
    # Instantiates a client
    translate_client = translate.Client()

    # The text to translate
    text = u'Hello, world!'
    # The target language
    target = 'ru'

    # Translates some text into Russian
    translation = translate_client.translate(text, target_language=target)

    print(u'Text: {}'.format(text))
    print(u'Translation: {}'.format(translation['translatedText']))
    """


def get_immediate_subdirectories(directory: str):
    return [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]


def minify_po_files(path: str, encoding: str = "utf8", print_output: bool = False, translate_now: bool = False):
    langs = get_immediate_subdirectories(path)
    langs = ["zh_Hans"]
    langs = ["de"]
    for lang in langs:
        with open(path + lang + "/LC_MESSAGES/django.po", encoding=encoding) as file:
            lines_all = []
            skip = False
            fuzzy = False
            # Add all lines to a list but ignore all fuzzy msgstr
            for line in file:
                if line.startswith("#") and "fuzzy" in line:
                    fuzzy = True
                if line.startswith("#: ."):
                    fuzzy = False
                    skip = False

                if fuzzy:
                    if not skip:
                        if line.startswith('msgstr "'):
                            lines_all.append('msgstr ""')
                            skip = True
                        else:
                            lines_all.append(line)
                    else:
                        lines_all.append("# skipped")
                else:
                    lines_all.append(line)



        lines = []
        skip = True
        fuzzy = False
        # Add all lines to a list
        first = True
        for line in lines_all:
            if not line.startswith("#"):
                if line.startswith('msgid "'):
                    if line.startswith('msgid ""') and first:
                        first = False
                        skip = True
                    else:
                        skip = False
                if skip:
                    if not line.startswith('"'):
                        lines.append(line.rstrip())
                elif line.startswith('msgstr'):
                    lines.append(line.rstrip())
                else:
                    lines.append(line.rstrip())

        lines.pop(0)
        lines.pop(0)

        required_lines = [
            '# Copyright (C) 2017-2018 LOLNAMES.GG',
            '# This file is distributed under the same license as the PACKAGE package.',
            '#',
            '#, fuzzy',
            'msgid ""',
            'msgstr ""',
            '"MIME-Version: 1.0\\n"',
            '"Content-Type: text/plain; charset=UTF-8\\n"',
            '"Content-Transfer-Encoding: 8bit\\n"',
        ]

        lines = required_lines + lines

        finished_lines = []
        building_line_msgid = False
        building_line_msgstr = False
        part_line = ''
        for line in lines:
            if line == 'msgid ""':
                building_line_msgid = True
            elif building_line_msgid:
                if line.startswith('"'):
                    part_line = part_line + line[1:-1]
                else:
                    building_line_msgid = False
                    finished_lines.append('msgid "' + part_line + '"')
                    part_line = ''
                    finished_lines.append(line)
            elif line == 'msgstr ""':
                building_line_msgstr = True
            elif building_line_msgstr:
                if line.startswith('"'):
                    part_line = part_line + line[1:-1]
                else:
                    building_line_msgstr = False
                    finished_lines.append('msgstr "' + part_line + '"')
                    part_line = ''
                    finished_lines.append(line)
            else:
                print(line)
                finished_lines.append(line)

        if finished_lines[len(finished_lines) - 1].startswith('msgid "'):
            finished_lines.append('msgstr ""')

        for line in finished_lines:
            pass#print(line)

        exit(11)
        with open(path + lang + "/LC_MESSAGES/django.po", "w", encoding=encoding) as output:
            for line in finished_lines:
                output.write(line + "\n")

    total = -1
    not_translated = -1

    # TODO make dynamic
    lang_names = ["Danish", "German", "Spanish", "Estonian", "Finnish", "French", "Hungarian", "Indonesian", "Italian",
                  "Japanese", "Korean", "Malay", "Dutch", "Norwegian", "Polish", "Portuguese", "Romanian", "Russian",
                  "Serbian", "Swedish", "Blank Template", "Thai", "Tagalog", "Turkish", "Ukrainian", "Vietnamese",
                  "Simplified Chinese", "Traditional Chinese", ]
    template = ""
    for lang, name in zip(langs, lang_names):
        with open(path + lang + "/LC_MESSAGES/django.po", encoding=encoding) as file:
            for line in file:
                if line.startswith('msgid "'):
                    line_to_translate = line[7:-2]
                    total = total + 1

                if line.startswith('msgstr ""'):
                    if translate_now:
                        translate_po_files(lang, line_to_translate)
                    not_translated = not_translated + 1

        if -100 * not_translated / total + 100 == 100:
            tick = "✔"
        elif -100 * not_translated / total + 100 != 0:
            tick = "➖"
        else:
            tick = "❌"

        # Used for creating part of the .md file for: https://github.com/hingston/lolnames.gg
        if print_output:
            if lang != "template":
                percent = -100 * not_translated / total + 100
                print(
                    "| {0} | [{1}](https://raw.githubusercontent.com/hingston/lolnames.gg/master/locale/{0}/LC_MESSAGES/django.po) | {2} {3:.2f}% |".format(
                        lang,
                        name,
                        tick,
                        percent))
            else:
                template = "| | [{1}](https://raw.githubusercontent.com/hingston/lolnames.gg/master/locale/{0}/LC_MESSAGES/django.po) | |".format(
                    lang,
                    name)

        total = -1
        not_translated = -1
    if print_output:
        print(template)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("$ python minify_po_files.py",
                                     description="removes all unnecessary lines from .po files")
    parser.add_argument("path", type=str, help="path of Django locale directory")
    parser.add_argument("-p", "--print", help="print percentage translated for readme.md", action="store_true")
    parser.add_argument("-e", "--encoding", type=str, help="encoding, default='utf8'", default="utf8")
    parser.add_argument("-t", "--translate", help="translate with Google Translate API", action="store_true")

    args = parser.parse_args()

    # has to be run twice TODO make it only require once
    minify_po_files(args.path, encoding=args.encoding)
    minify_po_files(args.path, encoding=args.encoding, print_output=args.print, translate_now=args.translate)
