from soldat_extmod_api.soldat_bridge import PAGE_READWRITE, MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READ
from soldat_extmod_api.graphics_helper.vector_utils import Vector2D
import struct


class MapManager:
    class RaycastResult:
        def __init__(self, hit_result: bool, distance: float, hit_point: Vector2D):
            self.hit_result = hit_result
            self.distance = distance
            self.hit_point = hit_point

        @classmethod
        def from_bytes(cls, result_bytes: bytes):
            return cls(hit_result=bool.from_bytes(result_bytes[0:1], byteorder="little"),
                       distance=struct.unpack("f", result_bytes[1:5])[0],
                       hit_point=Vector2D.from_bytes(result_bytes[5:]))

    @staticmethod
    def raycast(mod_api, a: Vector2D, b: Vector2D, distance: float, max_distance: float, 
                player=False, flag=False, bullet=True, check_collider=False, team = b"\x00") -> RaycastResult:
        soldat_bridge = mod_api.soldat_bridge
        assembler = mod_api.assembler
        mem_block: int = soldat_bridge.allocate_memory(32, MEM_COMMIT, PAGE_READWRITE)
        if mem_block:
            soldat_bridge.write(mem_block, a.to_bytes())
            soldat_bridge.write(mem_block+8, b.to_bytes())
            soldat_bridge.write(mem_block+16, struct.pack("f", distance))
            soldat_bridge.write(mem_block+20, struct.pack("f", max_distance))
            soldat_bridge.write(mem_block+24, player.to_bytes())
            soldat_bridge.write(mem_block+25, flag.to_bytes())
            soldat_bridge.write(mem_block+26, bullet.to_bytes())
            soldat_bridge.write(mem_block+27, check_collider.to_bytes())
            soldat_bridge.write(mem_block+28, team)

            code = f'''
            push dword ptr ds:[0x{(mem_block+16).to_bytes(4, "big").hex()}]
            push 0x{struct.pack("f", max_distance).hex()}
            push 0x{player.to_bytes().hex()}
            push 0x{flag.to_bytes().hex()}
            push 0x{bullet.to_bytes().hex()}
            push 0x{check_collider.to_bytes().hex()}
            push 0x{team.hex()}
            mov ecx, dword ptr ds:[0x{mem_block.to_bytes(4, "big").hex()}]
            mov edx, dword ptr ds:[0x{(mem_block+8).to_bytes(4, "big").hex()}]
            mov eax, dword ptr ds:[tpolymap]
            call TPolyMap.RayCast
            mov byte ptr ds:[0x{(mem_block+29).to_bytes(4, "big").hex()}], al
            xor eax, eax
            call RtlExitUserThread
            '''

            print(code)
            
            _dummy_assembly = assembler.assemble(code, 0)
            code_addr = soldat_bridge.allocate_memory(len(_dummy_assembly), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READ)
            code_assembled = assembler.assemble(code, code_addr)
            soldat_bridge.write(code_addr, code_assembled)
            soldat_bridge.execute(code_addr, None, True)

            result_bytes = soldat_bridge.read(mem_block+29, 1)
            result_bytes += soldat_bridge.read(mem_block+16, 4) 
            result_bytes += soldat_bridge.read(mem_block+8, 8)

            soldat_bridge.free_memory(mem_block)

            return MapManager.RaycastResult.from_bytes(result_bytes)