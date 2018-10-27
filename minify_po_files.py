"""Removes all unnecessary lines from .po files.

Created by William Hingston on 16/09/2018.

See:
    $ python minify_po_files.py -h
"""

import argparse
import os

from google.cloud import translate

translate_client = translate.Client()


def translate_po_files(lang: str, english_str: str):
    translation = translate_client.translate(english_str, target_language=lang)

    print(english_str)
    print(translation['translatedText'] + "\n")

    return translation['translatedText']


def get_immediate_subdirectories(directory: str):
    return [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]


def minify_po_files(path: str, encoding: str = "utf8", print_output: bool = False, translate: bool = False):
    langs = get_immediate_subdirectories(path)
    # langs = ["de"]
    for lang in langs:

        with open(path + lang + "/LC_MESSAGES/django.po", encoding=encoding) as file:

            lines_all = []
            skip = False
            fuzzy = False
            first = True
            # Add all lines to a list but ignore all fuzzy msgstr
            for line in file:
                if line.startswith("#") and "fuzzy" in line:
                    if first:
                        first = False
                    else:
                        fuzzy = True
                if line.startswith("#: ."):
                    if fuzzy:
                        lines_all.append('\n')
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
            '\n'
        ]

        finished_lines = []
        part_line = ''
        for line in lines:
            if line.startswith('msgstr ""'):
                if part_line != '':
                    finished_lines.append(part_line + '"')
                part_line = 'msgstr "'
            elif line.startswith('msgid ""'):
                if part_line != '':
                    finished_lines.append(part_line + '"')
                part_line = 'msgid "'
            elif line.startswith('"'):
                part_line = part_line + line[1:-1]
            else:
                if part_line != '':
                    finished_lines.append(part_line + '"')
                    part_line = ''
                finished_lines.append(line)

        if finished_lines[len(finished_lines) - 1].startswith('msgid "'):
            finished_lines.append('msgstr ""')

        translated_lines = []

        tokens = {"%(name)s": "NAME_STR",
                  "%(num_variants)s": "111111",
                  "%(display_name)s": "DISPLAY_STR",
                  "%(summoner_name)s": "SUMMONER_STR",
                  "%(account_id)s": "222222",
                  "%(number)s": "333333",
                  "%(months)s": "444",
                  "%(days)s": "555",
                  "%(region)s": "REGION_STR",
                  "%(page_title)s": "PAGE_STR", }

        # TODO use threads for this
        if translate and lang != "template":

            if lang == "zh_Hans":
                google_lang = "zh-CN"
            elif lang == "zh_Hant":
                google_lang = "zh-TW"
            else:
                google_lang = lang

            english_str = ""
            for line in finished_lines:
                if line.startswith('msgid "'):
                    english_str = line[7:-1]
                    translated_lines.append(line)
                elif line == 'msgstr ""':
                    if "%(" not in english_str:
                        translated_lines.append('msgstr "' + translate_po_files(google_lang, english_str) + '"')
                    else:
                        for key, token in tokens.items():
                            english_str = english_str.replace(key, token)
                        translated_str = translate_po_files(google_lang, english_str)
                        # print(english_str)
                        for key, token in tokens.items():
                            translated_str = translated_str.replace(token, key)
                        # print(translated_str + "\n")
                        translated_lines.append('msgstr "' + translated_str + '"')
                else:
                    translated_lines.append(line)
        else:
            translated_lines = finished_lines

        with open(path + lang + "/LC_MESSAGES/django.po", "w", encoding=encoding) as output:
            for line in required_lines:
                output.write(line + "\n")
            for line in translated_lines:
                if line.startswith('msgid'):
                    output.write(line.rstrip() + "\n")
                elif line.startswith('msgstr'):
                    output.write(line.rstrip() + "\n" + "\n")

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
                    total = total + 1

                if line.startswith('msgstr ""'):
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
                    "| {0} | [{1}](https://raw.githubusercontent.com/hingston/lolnames.gg/master/locale/{0}/LC_MESSAGES/django.po) | {2} {3:.2f}% | ❌ |".format(
                        lang,
                        name,
                        tick,
                        percent))
            else:
                template = "| | [{1}](https://raw.githubusercontent.com/hingston/lolnames.gg/master/locale/{0}/LC_MESSAGES/django.po) | | |".format(
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
    parser.add_argument("-t", "--translate", help="print percentage translated for readme.md", action="store_true")
    args = parser.parse_args()

    # has to be run twice TODO make it only require once
    minify_po_files(args.path, encoding=args.encoding)
    minify_po_files(args.path, encoding=args.encoding, print_output=args.print, translate=args.translate)
