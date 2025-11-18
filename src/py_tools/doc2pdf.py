"""convert Word file (.doc, .docx) to PDF file (.pdf)"""

import platform

if platform.platform() != "Windows":
    print("only support with Windows Word")
    exit(1)

import glob
import os.path
from itertools import chain
from pathlib import Path
from typing import Iterable, Sequence

from win32com import client

# available format code
# wdFormatDocument = 0
# wdFormatDocument97 = 0
# wdFormatDocumentDefault = 16
# wdFormatDOSText = 4
# wdFormatDOSTextLineBreaks = 5
# wdFormatEncodedText = 7
# wdFormatFilteredHTML = 10
# wdFormatFlatXML = 19
# wdFormatFlatXMLMacroEnabled = 20
# wdFormatFlatXMLTemplate = 21
# wdFormatFlatXMLTemplateMacroEnabled = 22
# wdFormatHTML = 8
# wdFormatPDF = 17
# wdFormatRTF = 6
# wdFormatTemplate = 1
# wdFormatTemplate97 = 1
# wdFormatText = 2
# wdFormatTextLineBreaks = 3
# wdFormatUnicodeText = 7
# wdFormatWebArchive = 9
# wdFormatXML = 11
# wdFormatXMLDocument = 12
# wdFormatXMLDocumentMacroEnabled = 13
# wdFormatXMLTemplate = 14
# wdFormatXMLTemplateMacroEnabled = 15


def _convert(word, path: Path) -> None:
    try:
        doc_abspath = path.absolute()
        doc = word.Documents.Open(str(doc_abspath))
        pdf_abspath = doc_abspath.with_suffix(".pdf")
        doc.SaveAs(str(pdf_abspath), 17)  # ref: above code list
        print(f"done: {path}")
    except Exception as e:
        print(e)


def convert(paths: Iterable[Path]) -> None:
    word = client.DispatchEx("Word.Application")

    for path in paths:
        _convert(word, path)

    word.Quit()


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "file",
        nargs="+",
        type=str,
        help="Word file (.doc, .docx), glob supports",
    )

    args = parser.parse_args()
    args_file: Sequence[str] = args.file  # type:ignore

    paths = map(
        Path,
        filter(os.path.isfile, chain.from_iterable(map(glob.iglob, args_file))),
    )
    convert(paths)
