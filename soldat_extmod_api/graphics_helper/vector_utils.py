from struct import pack, unpack

class Vector2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"{self.x}, {self.y}"

    def __eq__(self, __o: object) -> bool:
        if (type(self) == None) & (type(__o) == None):
            return True
        
        ret = False
        if (type(self) == Vector2D) & (type(__o) == Vector2D):
            if (self.x == __o.x) & (self.y == __o.y):
                ret = True
        return ret

    def __ne__(self, __o: object) -> bool:
        if (type(self) == None) & (type(__o) == None):
            return False

        ret = True
        if (type(self) == Vector2D) & (type(__o) == Vector2D):
            if (self.x == __o.x) & (self.y == __o.y):
                ret = False
        return ret
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __iadd__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def add(self, v):
        return Vector2D(self.x + v.x, self.y + v.y)
    
    def sub(self, v):
        return Vector2D(self.x - v.x, self.y - v.y)

    def to_bytes(self, endianness: str = "<"):
        return pack(endianness+"ff",self.x, self.y)
    
    def __neg__(self):
        return Vector2D(-self.x, -self.y)

    @classmethod
    def zero(cls):
        return cls(0.0, 0.0)
    
    @classmethod
    def from_bytes(cls, vector2d_bytes: bytes):
        return cls(*unpack("ff", vector2d_bytes))

class Vector2Ds:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"{self.x}, {self.y}"

    def __eq__(self, __o: object) -> bool:
        if (type(self) == None) & (type(__o) == None):
            return True
        
        ret = False
        if (type(self) == Vector2Ds) & (type(__o) == Vector2Ds):
            if (self.x == __o.x) & (self.y == __o.y):
                ret = True
        return ret

    def __ne__(self, __o: object) -> bool:
        if (type(self) == None) & (type(__o) == None):
            return False

        ret = True
        if (type(self) == Vector2Ds) & (type(__o) == Vector2Ds):
            if (self.x == __o.x) & (self.y == __o.y):
                ret = False
        return ret
    
    def __add__(self, other):
        return Vector2Ds(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2Ds(self.x - other.x, self.y - other.y)

    def __iadd__(self, other):
        return Vector2Ds(self.x + other.x, self.y + other.y)

    def add(self, v):
        return Vector2Ds(self.x + v.x, self.y + v.y)
    
    def sub(self, v):
        return Vector2Ds(self.x - v.x, self.y - v.y)

    def to_bytes(self):
        return pack("hh",self.x, self.y)
    
    def __neg__(self):
        return Vector2Ds(-self.x, -self.y)

    @classmethod
    def zero(cls):
        return cls(0, 0)

class Vector3D:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self) -> str:
        return f"{self.x}, {self.y}, {self.z}"

    def __eq__(self, __o: object) -> bool:
        if (type(self) == None) & (type(__o) == None):
            return True
        
        ret = False
        if (type(self) == Vector3D) & (type(__o) == Vector3D):
            if (self.x == __o.x) & (self.y == __o.y) & (self.z == __o.z):
                ret = True
        return ret

    def __ne__(self, __o: object) -> bool:
        if (type(self) == None) & (type(__o) == None):
            return False

        ret = True
        if (type(self) == Vector3D) & (type(__o) == Vector3D):
            if (self.x == __o.x) & (self.y == __o.y) & (self.z == __o.z):
                ret = False
        return ret
    
    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z + other.z)

    def __iadd__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def add(self, v):
        return Vector3D(self.x + v.x, self.y + v.y, self.z + v.z)
    
    def sub(self, v):
        return Vector3D(self.x - v.x, self.y - v.y, self.z - v.z)

    def to_bytes(self):
        return pack("fff",self.x, self.y, self.y)
    
    def __neg__(self):
        return Vector3D(-self.x, -self.y, -self.z)
    
    @classmethod
    def zero(cls):
        return cls(0.0, 0.0, 0.0)