# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 18:11:38 2024

@author: Steven, Hsin
@email: steveh8758@gmail.com
"""

import re
from termcolor import colored
import win32clipboard

def _invisible_char_crypt(input_str: str, method: str = "auto") -> str:
    """
    Encrypts or decrypts text using invisible Unicode characters.

    Args:
        input_str (str): The text to be encrypted or decrypted.
        method (str, optional): The encryption/decryption method. Defaults to "auto".
            - "auto": Automatically determines whether to encrypt or decrypt based on
                      the presence of invisible characters in the input string.
            - "enc": Encrypts the text.
            - "dec": Decrypts the text.
            - "dec_keep_origin": Decrypts the text while preserving any non-hidden characters
                                 encountered during decryption.

    Returns:
        str: The encrypted or decrypted text.

    Raises:
        ValueError: If an invalid method is specified.
    """
    VALID_METHODS = {"auto", "enc", "dec", "dec_keep_origin"}
    if method not in VALID_METHODS:
        raise ValueError("Invalid method specified. Choose 'auto', 'enc', 'dec' or 'dec_keep_origin'.")

    zwsp, zwnj = '\u200B', '\u200C'

    def enc(hide_str: str) -> str:
        """
        Encodes text as a sequence of invisible characters based on its binary representation.

        Args:
            hide_str (str): The text to be hidden.

        Returns:
            str: The encoded string of invisible characters.
        """
        return ''.join(
            zwnj if bit == '1' else zwsp
            for char in hide_str.encode('utf-8')
            for bit in format(char, '08b')
        )

    def dec(hide_str: str) -> str:
        """
        Decodes a sequence of invisible characters back to the original text.

        Args:
            hide_str (str): The string of invisible characters.

        Returns:
            str: The decoded text.
        """
        rt = ""
        tmp = ""
        for c in hide_str:
            if c == zwnj:
                tmp += "1"
            elif c == zwsp:
                tmp += "0"
            else:
                if method == "dec_keep_origin":
                    if tmp == "":
                        rt += c
                    else:
                        rt += bytearray(int(tmp[i:i + 8], 2) for i in range(0, len(tmp), 8)).decode('utf-8', errors='ignore') + c
                        tmp = ""
                else:
                    pass
        if tmp != "":
            rt = bytearray(int(tmp[i:i + 8], 2) for i in range(0, len(tmp), 8)).decode('utf-8', errors='ignore')
        return rt


    if method == "auto":
        method = "dec" if zwsp in input_str or zwnj in input_str else "enc"

    return enc(input_str) if method == "enc" else dec(input_str)

def set_clipboard(text):
    """
    Copies text to the clipboard.

    Args:
        text (str): The text to be copied.
    """
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()


def main(text:str) -> str:
    """
    The main function for text encryption/decryption and clipboard interaction.

    Args:
        text (str): The input text.

    Returns:
        str: The encrypted text (if encryption was performed) or the original text.
    """
    pattern = r'\(\((.*?)\)\)'
    matches = re.findall(pattern, text)
    # others = [part for part in re.split(pattern, text) if part not in matches]
    output = text.replace("((", "").replace("))", "")
    for i in matches:
        output = output.replace(i, _invisible_char_crypt(i, "enc"))
    set_clipboard(output)
    return output

if __name__ == '__main__':
    text = ""
    if text == "":
        print("\n\n\n請使用 (()) 把要隱藏的字括起來!")
        res = main(str(input(": ")))
    else:
        res = main(text)
    print(f'\n\n{colored("結果已經複製在你的剪貼簿了!", "light_magenta")}\n加密後結果: "{colored(res, "yellow")}"\n\n')
    dec_str = _invisible_char_crypt(str(input("請輸入欲解密內容: ")), "dec_keep_origin")
    print(f'解密後結果: "{colored(dec_str, "light_cyan")}"\n\n\n')
    input()
