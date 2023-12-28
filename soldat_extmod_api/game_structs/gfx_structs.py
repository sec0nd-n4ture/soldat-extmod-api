from struct import pack

'''
TGfxSprite -- 0x30 size (48 bytes)
   i     i       i         i          f         i         f        f        f        f          ptr        ptr
|  x  |  y  |  width  |  height  |  scale  |  delay  |  left  |  right  |  top  |  bottom  |  texture  |  next  |
   4     4       4         4          4         4         4        4        4        4           4          4    
'''

class ImageData:
    def __init__(self, file_name: str, width: int, height: int, components: int, pData: bytes):
        self.file_name = file_name
        self.width = width
        self.height = height
        self.components = components # RGBA = 4
        self.pData = pData

class ImageDataCache:
    def __init__(self):
        self.cache: dict[str, ImageData] = {}

    def add_to_cache(self, idat: ImageData):
        self.cache[idat.file_name] = idat

    def get_from_cache(self, file_name: str) -> ImageData:
        return self.cache.get(file_name)

    def check_cache(self, file_name: str) -> bool:
        return file_name in self.cache

class TGfxRect:
    def __init__(self, left : float, right : float, top : float, bottom : float):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def to_bytes(self):
        return pack("ffff", self.left, self.right, self.top, self.bottom)
    

class TGfxSprite:
    def __init__(self,
        x: int,
        y: int,
        width: int,
        height: int,
        scale: float,
        delay: int,
        rect: TGfxRect,
        texture: bytes,
        next: bytes
    ):
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.scale: float = scale
        self.delay: int = delay
        self.rect: TGfxRect = rect
        self.texture: bytes = texture
        self.next: bytes = next

    def to_bytes(self):
        return pack("IIIIfI",  self.x, self.y,
                               self.width, self.height,
                               self.scale, self.delay) \
                             + self.rect.to_bytes() \
                             + self.texture \
                             + self.next