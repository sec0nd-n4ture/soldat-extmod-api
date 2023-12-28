from struct import pack


'''
Colors are in ARGB
'''
class TPlayer:
    def __init__(self):
        self.Name: int = 0
        self.hwid: int = 0
        self.IP: int = 0
        self.Port: int = 0
        self.Color1: int = 0x01020304
        self.Color2: int = 0x05060708
        self.SkinColor: int = 0x09101112
        self.HairColor: int = 0x13141516
        self.JetColor: int = 0x17181920
        self.Kills: int = 0
        self.Deaths: int = 0
        self.Flags: bytes = b"\x00"
        self.PingTicks: int = 0
        self.PingTicksB: int = 0
        self.PingTime: int = 0
        self.Ping: int = 0
        self.Team: bytes = b"\x00"
        self.ControlMethod: bytes = b"\x00"
        self.State: bytes = b"\x00"
        self.Cheat: bytes = b"\x00"
        self.Chain: bytes = b"\x00"
        self.HeadCap: bytes = b"\x00"
        self.HairStyle: bytes = b"\x00"
        self.SecWep: bytes = b"\x00"
        self.Camera: bytes = b"\x00"
        self.Muted: bytes = b"\x00"

    def to_bytes(self):
        return pack("IIIIIIIIIIIcxxxIIIIccccccccccxx", 
                   self.Name,
                   self.hwid,
                   self.IP,
                   self.Port,
                   self.Color1,
                   self.Color2,
                   self.SkinColor,
                   self.HairColor,
                   self.JetColor,
                   self.Kills,
                   self.Deaths,
                   self.Flags,
                   self.PingTicks,
                   self.PingTicksB,
                   self.PingTime,
                   self.Ping,
                   self.Team,
                   self.ControlMethod,
                   self.State,
                   self.Cheat,
                   self.Chain,
                   self.HeadCap,
                   self.HairStyle,
                   self.SecWep,
                   self.Camera,
                   self.Muted)