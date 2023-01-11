from typing import List, Sequence, Tuple, Union

from altic.rpmspec.utils import snake_to_capital


class Directive:
    """
    Simple RPM Spec directive.
    
    For example:
    >>> str(Directive("version", "1.0.0"))
    "Version: 1.0.0"
    
    Attributes:
        key (str): name of directive
        value (str): value of directive
        description (str, optional): description of directive.
        If set, serialized as a comment line above directive.

    Returns:
        Directive: created directive object
    """
    key: str = ""
    value: Union[str, List[str]] = ""
    description: str = ""
    
    def __init__(self, key: str, value: Union[str, List[str]] = "", description: str = ""):
        self.key = key
        self.value = value
        self.description = description
    
    def set(self, value: Union[str, List[str]], *, description: str = "") -> None:
        """
        Sets value of directive.

        Args:
            value (Union[str, List[str]]): value to set
            description: (str, optional): description of directive to set
        """
        self.value = value
        if description:
            self.description = description
    
    @property
    def display_key(self) -> str:
        """
        Representation of key in serialized RPM spec.
        
        E.g. build_requires key display representation is "BuildRequires"
        
        Returns:
            str: RPM spec-like representation of key.
        """
        return snake_to_capital(self.key)
    
    @property
    def comment(self):
        """
        Comment of description value in RPM spec.

        Returns:
            str: RPM spec comment line with description as comment content.
        """
        return f"# {self.description}" if self.description and self.value else ""

    @property
    def line(self):
        """
        Representation of single line in directive.
        
        Example:
        >>> Directive('version', '1.1.1').line
        "Version: 1.1.1"
        
        Returns:
            str: Representation of single line in directive,
        """
        return f"{self.display_key}: {self.value}" if self.value else ""
    
    def serialize(self) -> str:
        return "\n".join([self.comment, self.line]).strip()
    
    def as_dict(self):
        return {self.key: self.value}
    
    def as_tuple(self) -> Tuple[str, Union[str, List[str]]]:
        return (self.key, self.value)
    
    @classmethod
    def from_dict(cls, source_dict: dict) -> "Directive":
        k, v = list(*source_dict.items())
        return cls(k, value=v)
        
    def __str__(self):
        return self.serialize()
    
    def __repr__(self):
        return f"<Directive key={self.key} value={self.value}>"
    

class ListDirective(Directive):
    """
    RPM Spec list directive.
    
    For example:
    >>> str(ListDirective("requires", ['python', 'linux', 'something']))
    "Requires: python linux something"
    
    >>> str(ListDirective("requires", ['python', 'linux', 'something'], separator=","))
    "Requires: python,linux,something"
    
    Attributes:
        key (str): name of directive
        value (Sequence[str]): several values of directive
        description (str, optional): description of directive.
        If set, serialized as a comment line above directive.
        separator (str): separator between serialized values of directive.

    Returns:
        ListDirective: created list directive object
    """
    separator: str = ""
    
    def __init__(self, key: str, value: Sequence[str] = None, description: str = "", separator: str = " ", pre: bool = False):
        if value is None:
            value = list()
        super().__init__(key, value, description)
        self.separator = separator
    
    def line(self, item: str = "", **params: dict) -> str:
        return item
    
    def serialize(self) -> str:
        if not isinstance(self.value, Sequence):
            raise ValueError("List directive value should be any of: list, tuple, set")
        serialized_directive = self.separator.join([
            self.line(item, idx=idx)
            for idx, item in enumerate(self.value)
            if item
        ]).strip()
        return f"{self.display_key}: {serialized_directive}"

    def __str__(self) -> str:
        return self.serialize()
        
    
class IterDirective(ListDirective):
    """
    RPM Spec iterable list directive.
    
    Example:
    >>> str(IterDirective("Patch", ['patch-1.patch', 'patch-2.patch']))
    "Patch0: patch-1.patch"
    "Patch1: patch-2.patch"
    
    Attributes:
        key (str): name of directive
        value (Sequence[str]): several values of directive
        description (str, optional): description of directive.
        If set, serialized as a comment line above directive.
        
    Notes:
        The changing of separator of iterable list directive will give no results.

    Returns:
        IterDirective: created iterable list directive object
    """
    def __init__(self, key: str, value: Sequence[str] = None, description: str = ""):
        if not value:
            value = list()
        super().__init__(key, value, description)
        
    def line(self, item: str = "", **params: dict) -> str:
        """
        Representation of single line in directive.

        Args:
            item (str, optional): rendered value of field. Defaults to "".

        Returns:
            str: serialized line of directive
        """
        if not item:
            return ""
        return f"{self.display_key}{params.get('idx')}: {item}"
    
    def serialize(self) -> str:
        if not isinstance(self.value, Sequence):
            raise ValueError("List directive value should be any of: list, tuple, set")
        return "\n".join([
            self.line(item, idx=idx)
            for idx, item in enumerate(self.value)
            if item
        ]).strip()
    
    def __str__(self) -> str:
        return self.serialize()


class MacroDirective(ListDirective):
    """
    RPM spec macro directive
    
    Example:
    >>> str(Macro("prep", ['#!/bin/bash', 'echo "Hello World"']))
    "%prep"
    "#!/bin/bash"
    'echo "Hello World"'
    
    Attributes:
        key (str): name of macro. In that case will be the name of macros.
        value (Sequence[str]): several values of directive. Body of macro.
        description (str, optional): description of directive.
        If set, serialized as a comment line above directive.

    Returns:
        MacroDirective: created macro directive object
    """
    def __init__(self, key: str, value: Sequence[str] = None, description: str = ""):
        super().__init__(key, value, description, "\n")
    
    def line(self, item: str = "", **params: dict) -> str:
        return item
    
    def serialize(self) -> str:
        macro_header = f"\n\n%{self.key}"
        macro_body = self.separator.join([
            self.line(item, idx=idx)
            for idx, item in enumerate(self.value)
            if item
        ]).strip()
        return "\n".join([macro_header, macro_body])
    
    def __str__(self) -> str:
        return self.serialize()


class RPMSpecSection:
    _entries = {}

    def serialize(self):
        return "\n".join(
            [
                str(f)
                for f in self._entries.values()
                if isinstance(f, Directive) and f.value
            ]
        )
    

class RPMSpecPreamble(RPMSpecSection):
    
    def init_main_directives(self):
        self._entries.update({
            "name": Directive("name"),
            "version": Directive("version"),
            "release": Directive("release"),
            "summary": Directive("summary"),
            "license": Directive("license"),
            "url": Directive("url"),
            "packager": Directive("packager"),
            "build_arch": Directive("build_arch"),
            "exclude_arch": Directive("exclude_arch"),
        })
    
    def init_list_directives(self):
        self._entries.update({
            "build_requires": ListDirective("build_requires"),
            "requires": ListDirective("requires"),
            "conflicts": ListDirective("conflicts"),
            "obsoletes": ListDirective("obsoletes"),
        })
    
    def init_iter_directives(self):
        self._entries.update({
            "sources": IterDirective("source"),
            "patches": IterDirective("patch"),
        })
    
    def __init__(self):
        self.init_main_directives()
        self.init_iter_directives()
        self.init_list_directives()
    
    def __str__(self):
        return self.serialize()
    

class RPMSpecBody(RPMSpecSection):
    
    def init_macro_directives(self):
        self._entries.update({
            "description": MacroDirective("description"),
            "prep": MacroDirective("prep"),
            "changelog": MacroDirective("changelog"),
            "build": MacroDirective("build"),
            "install": MacroDirective("install"),
            "check": MacroDirective("check"),
            "files": MacroDirective("files"),
        })
    
    def __init__(self):
        self.init_macro_directives()
    
    def __str__(self):
        return self.serialize()


class RPMSpec:
    
    def __init__(self, **kwargs):
        self.preamble = RPMSpecPreamble()
        self.body = RPMSpecBody()
        self.populate_sections(**kwargs)
    
    def populate_sections(self, **params):
        if not params:
            return
        sections = [s for s in self.__dict__.values() if isinstance(s, RPMSpecSection)]
        for section in sections:
            for k, v in params.items():
                if k in section._entries:
                    section._entries[k].set(v)
    
    def serialize(self) -> str:
        """
        Serialization of all spec fields into single string.

        Returns:
            str: rpm spec in string
        """
        return "\n".join([str(self.preamble), str(self.body)])

    def __str__(self) -> str:
        return self.serialize()

