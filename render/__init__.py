from render.texture import defaultFont, Font


class InnerStringConfig:
    """
    这是内部类，外部不应直接使用
    """
    def __init__(self):
        self.string: str | None = None
        self.color: int = 0xffffffff
        self.background: int = 0xffffffff
        self.font: int = 0
        self.italic: bool = False
        self.bold: bool = False
        self.delete: bool = False
        self.underline: bool = False
    
    def clone(self) -> 'InnerStringConfig':
        ret: 'InnerStringConfig' = InnerStringConfig()
        ret.color = self.color
        ret.background = self.background
        ret.font = self.font
        ret.italic = self.italic
        ret.bold = self.bold
        ret.delete = self.delete
        ret.underline = self.underline
        return ret
    
    def appendString(self, string: str) -> None:
        if self.string is None:
            self.string = string
        else:
            self.string += string
        
    def __str__(self) -> str:
        return f'#{hex(self.color)[2:]}.{hex(self.background)[2:]}"' \
               f'"F{self.font}{"/" if self.italic else " "}' \
               f'{"=" if self.bold else " "}' \
               f'{"-" if self.delete else " "}' \
               f'{"_" if self.underline else " "}\n  ' \
               f'{self.string}'


class RenderableString:
    """
    用于风格化字符串输出。以反斜线开头
    \\#AARRGGBB
    \\.AARRGGBB背景色
    \\f<fontName>
    \\-删除线
    \\_下划线
    \\/斜体
    \\=粗体
    """
    
    def __init__(self, string: str):
        self.set: list[InnerStringConfig] = []
        self._parseAppend(string)
    
    def _parseAppend(self, string: str) -> None:
        config = InnerStringConfig()
        subs = string.split('\\')
        for i in subs:
            if config.string is not None:
                self.set.append(config)
                config = config.clone()
            if len(i) == 0:
                continue
            match i[0]:
                case '#':
                    if len(i) < 9:
                        continue
                    if len(i) > 9:
                        config.appendString(i[9:])
                    config.color = int(i[1:9], 16)
                    continue
                case '.':
                    if len(i) < 9:
                        continue
                    if len(i) > 9:
                        config.appendString(i[9:])
                    config.background = int(i[1:9], 16)
                case 'f':
                    if len(i) < 2:
                        continue
                    if len(i) > 2:
                        config.appendString(i[2:])
                    config.font = int(i[1])
                    continue
                case '-':
                    config.delete = True
                    if len(i) >= 1:
                        config.appendString(i[1:])
                    continue
                case '_':
                    config.underline = True
                    if len(i) >= 1:
                        config.appendString(i[1:])
                    continue
                case '/':
                    config.italic = True
                    if len(i) >= 1:
                        config.appendString(i[1:])
                    continue
                case '=':
                    config.bold = True
                    if len(i) >= 1:
                        config.appendString(i[1:])
                    continue
                case '\\':
                    config.appendString('\\')
                    continue
        if config.string is not None:
            self.set.append(config)
                
    def __str__(self):
        return '\n'.join([str(i) for i in self.set])
            
        
        

