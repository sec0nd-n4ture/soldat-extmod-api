from soldat_extmod_api.soldat_bridge import PAGE_READWRITE, MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READ
from soldat_extmod_api.graphics_helper.vector_utils import Vector2D
import struct


class MapManager:
    class RaycastResult:
        def __init__(self, hit_result: bool, distance: float):
            self.hit_result = hit_result
            self.distance = distance

        @classmethod
        def from_bytes(cls, result_bytes: bytes):
            return cls(hit_result=bool.from_bytes(result_bytes[0:1], byteorder="little"),
                       distance=struct.unpack("f", result_bytes[1:5])[0])

    @staticmethod
    def raycast(mod_api, a: Vector2D, b: Vector2D, distance: float, max_distance: float, 
                player=False, flag=False, bullet=True, check_collider=False, team = b"\x00") -> RaycastResult:
        soldat_bridge = mod_api.soldat_bridge
        assembler = mod_api.assembler
        mem_block: int = soldat_bridge.allocate_memory(64, MEM_COMMIT, PAGE_READWRITE)
        if mem_block:
            
            a_ptr = mem_block
            b_ptr = mem_block+8
            distance_ptr = mem_block+16
            raycast_result_ptr = mem_block+24
            a_bytes = a.to_bytes()
            b_bytes = b.to_bytes()

            soldat_bridge.write(distance_ptr, struct.pack(">f", distance))

            code = f'''
            sub esp, 0x2C
            push 0x{a_bytes[:4].hex()}
            push 0x{a_bytes[4:].hex()}
            mov eax, 0x{a_ptr.to_bytes(4, "big").hex()}
            call Vector2
            push 0x{b_bytes[:4].hex()}
            push 0x{b_bytes[4:].hex()}
            mov eax, 0x{b_ptr.to_bytes(4, "big").hex()}
            call Vector2
            push 0x{distance_ptr.to_bytes(4, "big").hex()}
            push 0x{struct.pack(">f", max_distance).hex()}
            push 0x{player.to_bytes().hex()}
            push 0x{flag.to_bytes().hex()}
            push 0x{bullet.to_bytes().hex()}
            push 0x{check_collider.to_bytes().hex()}
            push 0x{team.hex()}
            mov ecx, 0x{b_ptr.to_bytes(4, "big").hex()}
            mov edx, 0x{a_ptr.to_bytes(4, "big").hex()}
            mov eax, dword ptr ds:[tpolymap]
            call TPolyMap.RayCast
            mov byte ptr ds:[0x{raycast_result_ptr.to_bytes(4, "big").hex()}], al
            xor eax, eax
            call RtlExitUserThread
            '''
            
            _dummy_assembly = assembler.assemble(code, 0)
            code_addr = soldat_bridge.allocate_memory(len(_dummy_assembly), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READ)
            code_assembled = assembler.assemble(code, code_addr)
            soldat_bridge.write(code_addr, code_assembled)
            soldat_bridge.execute(code_addr, None, True)

            result_bytes = soldat_bridge.read(raycast_result_ptr, 1)
            result_bytes += soldat_bridge.read(distance_ptr, 4) 

            soldat_bridge.free_memory(mem_block)

            return MapManager.RaycastResult.from_bytes(result_bytes)