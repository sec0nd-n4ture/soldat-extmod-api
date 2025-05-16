push ebx
add esp, 0xFFFFFF8C
mov ebx,eax
push 0
mov eax, dword ptr ds:[screen_width]
fild dword ptr ds:[eax]
add esp, 0xFFFFFFFC
fstp dword ptr ss:[esp]
fwait 
push 0
mov eax, dword ptr ds:[screen_height]
fild dword ptr ds:[eax]
add esp,0xFFFFFFFC
fstp dword ptr ss:[esp]
fwait 
lea eax, dword ptr ss:[esp+0x10]
call GfxMat3Ortho
mov eax, esp
call GfxTransform
mov eax,dword ptr ds:[screen_width]
fild dword ptr ds:[eax]
add esp,0xFFFFFFFC
fstp dword ptr ss:[esp]
fwait 
mov eax,dword ptr ds:[screen_height]
fild dword ptr ds:[eax]
add esp,0xFFFFFFFC
fstp dword ptr ss:[esp]
fwait 
push 0x3F800000
push 0
mov dl,0xFF
mov eax, 0xFFFFFF
call RGBA
lea edx,dword ptr ss:[esp+0x34]
call GfxVertex
lea eax,dword ptr ss:[esp+0x24]
push eax
push 0
mov eax,dword ptr ds:[screen_height]
fild dword ptr ds:[eax]
add esp,0xFFFFFFFC
fstp dword ptr ss:[esp]
fwait 
push 0
push 0
mov dl, 0xFF
mov eax, 0xFFFFFF
call RGBA
lea edx,dword ptr ss:[esp+0x4C]
call GfxVertex
lea eax,dword ptr ss:[esp+0x3C]
push eax
mov eax,dword ptr ds:[screen_width]
fild dword ptr ds:[eax]
add esp,0xFFFFFFFC
fstp dword ptr ss:[esp]
fwait 
push 0
push 0x3F800000
push 0x3F800000
mov dl, 0xFF
mov eax, 0xFFFFFF
call RGBA
lea edx, dword ptr ss:[esp+0x64]
call GfxVertex
lea eax, dword ptr ss:[esp+0x54]
push eax
push 0
push 0
push 0
push 0x3F800000
mov dl, 0xFF
mov eax, 0xFFFFFF
call RGBA
lea edx, dword ptr ss:[esp+0x7C]
call GfxVertex
lea edx, dword ptr ss:[esp+0x6C]
mov eax, ebx
pop ecx
call GfxDrawQuad
add esp, 0x74
pop ebx
ret 