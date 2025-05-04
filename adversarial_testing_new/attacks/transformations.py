
import base64
import random
from typing import Dict, Callable

class StringTransformation:
    def __init__(self):
        self.morse_code = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
            'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
            'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
            'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
            'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
            'Z': '--..', ' ': '/'
        }
        
        self.homoglyphs = {
            'a': ['а', 'à', 'á'], 'e': ['е', 'é', 'è'],
            'i': ['і', 'í', 'ì'], 'o': ['о', 'ó', 'ò'],
            's': ['ѕ', 'ś', 'š'], 'l': ['ł', 'ĺ', 'ļ']
        }

        self.leet_map = {
            'a': '4', 'e': '3', 'i': '1',
            'o': '0', 's': '5', 't': '7'
        }

    def transform(self, text: str, method: str) -> str:
        """Apply specified transformation to text"""
        transform_map: Dict[str, Callable[[str], str]] = {
            # Reversal transformations
            "reversal": lambda x: x[::-1],
            "per-word reversal": self._per_word_reversal,
            "word-level reversal": self._word_level_reversal,
            
            # Ciphers
            "caesar_cipher": lambda x: self._caesar_cipher(x, 3),
            "rot13_cipher": lambda x: self._caesar_cipher(x, 13),
            "atbash_cipher": self._atbash_cipher,
            
            # Encoding
            "base64_encoding": lambda x: base64.b64encode(x.encode()).decode(),
            "binary_encoding": self._binary_encode,
            
            # Obfuscation
            "leetspeak": self._leetspeak,
            "morse_code": self._morse_code_encode,
            "homoglyph_confusion": self._homoglyph_confusion,
            "typos": self._add_typos,
            
            # Structural
            "vowel_repetition": self._vowel_repetition,
            "alternating_case": self._alternating_case,
            "palindrome": self._palindrome,
            "interleaving_delimiter": lambda x: '@'.join(x),
            "prefix_rotation": self._prefix_rotation,
            "spoonerism": self._spoonerism,
            "stuttering": self._stuttering,
            
            # Format wrappers
            "python_markdown": lambda x: f"```python\n{x}\n```",
            "json_encapsulation": lambda x: f'{{"text": "{x}"}}',
            "latex_wrapper": lambda x: f"\\documentclass{{article}}\\begin{{document}}{x}\\end{{document}}"
        }
        
        return transform_map.get(method.lower(), lambda x: x)(text)

    # Transformation helper methods
    def _per_word_reversal(self, text: str) -> str:
        return ' '.join(word[::-1] for word in text.split())

    def _word_level_reversal(self, text: str) -> str:
        return ' '.join(text.split()[::-1])

    def _caesar_cipher(self, text: str, shift: int) -> str:
        result = []
        for char in text:
            if char.isupper():
                result.append(chr((ord(char) + shift - 65) % 26 + 65))
            elif char.islower():
                result.append(chr((ord(char) + shift - 97) % 26 + 97))
            else:
                result.append(char)
        return ''.join(result)

    def _atbash_cipher(self, text: str) -> str:
        def transform_char(c):
            if c.isupper():
                return chr(90 - (ord(c) - 65))
            elif c.islower():
                return chr(122 - (ord(c) - 97))
            return c
        return ''.join(transform_char(c) for c in text)

    def _binary_encode(self, text: str) -> str:
        return ' '.join(format(ord(c), '08b') for c in text)

    def _leetspeak(self, text: str) -> str:
        return ''.join(self.leet_map.get(c.lower(), c) for c in text)

    def _morse_code_encode(self, text: str) -> str:
        return ' '.join(self.morse_code.get(c.upper(), '#') for c in text)

    def _homoglyph_confusion(self, text: str) -> str:
        return ''.join(random.choice(self.homoglyphs.get(c.lower(), [c])) for c in text)

    def _add_typos(self, text: str) -> str:
        typo_text = []
        for c in text:
            if random.random() < 0.3:
                typo_text.append(random.choice([c, c.upper(), '', c*2]))
            else:
                typo_text.append(c)
        return ''.join(typo_text)

    def _vowel_repetition(self, text: str) -> str:
        vowels = 'aeiouAEIOU'
        return ''.join(c*3 if c in vowels else c for c in text)

    def _alternating_case(self, text: str) -> str:
        return ''.join(c.upper() if i%2==0 else c.lower() for i,c in enumerate(text))

    def _palindrome(self, text: str) -> str:
        return text + text[::-1]

    def _prefix_rotation(self, text: str) -> str:
        return ' '.join(word[3:] + word[:3] if len(word)>3 else word for word in text.split())

    def _spoonerism(self, text: str) -> str:
        words = text.split()
        if len(words) >= 2:
            w1, w2 = words[0], words[1]
            new_w1 = w2[0] + w1[1:] if len(w1) > 0 else w1
            new_w2 = w1[0] + w2[1:] if len(w2) > 0 else w2
            return ' '.join([new_w1, new_w2] + words[2:])
        return text

    def _stuttering(self, text: str) -> str:
        return ' '.join(f"{word[:2]}-{word}" for word in text.split())
