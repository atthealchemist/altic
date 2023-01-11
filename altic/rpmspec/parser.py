
import re
import string
from typing import List

from altic.rpmspec.utils import capital_to_snake, plural


class RPMSpecParser:
    
    def parse_directive(self, line: str) -> dict:
        parsed_directive = {}
        if ":" in line and line[:1].isupper():
            key, value = line.split(":")
            parsed_directive[capital_to_snake(key)] = value.strip()
        return parsed_directive

    def parse_macro(self, header: str, body: List[str]) -> dict:
        body_lines = []
        for line in body:
            if any([self.is_line_directive(line), self.is_macro_directive(line)]):
                break
            if not line:
                continue
            body_lines.append(line)
        parsed_macro = {
            header.strip("%"): body_lines
        }
        return parsed_macro

    def parse_iter_directive(self, header: str, body: List[str]) -> dict:
        parsed_iter = {}
        rest_lines = [header] + body
        for line in rest_lines:
            if not self.is_iter_directive(line):
                break
            k, v = list(*self.parse_directive(line).items())
            plural_key = plural(k.rstrip(string.digits))
            if not parsed_iter.get(plural_key):
                parsed_iter[plural_key] = list()
            parsed_iter[plural_key].append(v.strip())
        return parsed_iter
        
    def parse_list_directive(self, line):
        parsed_list = {}
        for k, v in self.parse_directive(line).items():
            if " " in v:
                parsed_list[k] = v.split(" ")
        return parsed_list
    
    def is_line_directive(self, line: str) -> bool:
        return ":" in line and line[:1].isupper()
    
    def is_macro_directive(self, line: str) -> bool:
        return line.startswith("%") and line.islower()
    
    def is_iter_directive(self, line: str):
        return self.is_line_directive(line) and bool(re.search(r'(^[A-Z][a-zA-Z]+\d{1,2})', line))
    
    def is_list_directive(self, line: str):
        return self.is_line_directive(line) and bool(re.search(r'(^[A-Z][a-zA-Z]+s\b)', line))
        
    def parse(self, content: str) -> dict:
        parsed_spec = {}
        lines = content.strip().split("\n")
        for idx, line in enumerate(lines):
            rest_lines = lines[idx + 1:]
            if self.is_macro_directive(line):
                if rest_lines:
                    parsed_spec.update(
                        self.parse_macro(header=line, body=rest_lines)
                    )
            elif self.is_iter_directive(line):
                parsed_iter = self.parse_iter_directive(header=line, body=rest_lines)
                k, v = list(*parsed_iter.items())
                if k not in parsed_spec:
                    parsed_spec.update(parsed_iter)
                elif isinstance(v, str):
                    parsed_spec[k].append(v)
            elif self.is_list_directive(line):
                parsed_spec.update(self.parse_list_directive(line))
            elif self.is_line_directive(line):
                parsed_spec.update(self.parse_directive(line))
        return parsed_spec
