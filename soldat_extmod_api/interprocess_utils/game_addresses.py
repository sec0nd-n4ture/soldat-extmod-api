addresses = {
    3712077237: { # 1.7.1.1 local build
            "GfxCreateTexture": 0x005178A4,
            "RenderInterface": 0x005F51C8,
            "GfxDrawSprite": 0x0051848C,
            "GfxTextColor": 0x00519C44,
            "GfxTextShadow": 0x00519C58,
            "SetFontStyle": 0x00605D24,
            "GfxTextScale": 0x00519C34,
            "GfxDrawText": 0x00519FAC,
            "ifacebyte": b"\x3D",
            "Stbi_load_from_memory": 0x1470, # offset
            "camera_world_pos_x": 0x00907014,
            "camera_world_pos_y": 0x00907018,
            "cursor_screen_pos": 0x0062739C,
            "cursor_x_setter": 0x005741C0, # 2 nops to disable
            "cursor_y_setter": 0x005741CF,
            "game_width_half": 0x0061C588,
            "game_height_half": 0x0061C58C,
            "dxready": 0x0061C024,
            "CreateSprite": 0x0056FB0C,
            "CollisionCheck": 0x005C7238,
            "TransparencyUpdater": 0x005B4AD8,
            "ClientHandleSpecialMessage": 0x005E8C94,
            "LStrFromArray": 0x00404FB4,
            "FormKeyPress": 0x00589BD0,
            "player_base": 0x00907020,
            "player_sprite_base": 0x007A2710,
            "chat_show_flag": 0x0056F611,
            "current_map_name_length": 0x007B832C,
            "current_map_name": 0x007B832D,
            "own_id": 0x0069B82C,
            "ClientSendBullet": 0x005DCDFC,
            "client_tick_count": 0x00D2D44C,
            "CreateBullet": 0x00570490,
            "TSprite.Respawn": 0x005BB5B0,
            "dimousestate2": 0x00624B48,
            "tpolymap": 0x0061F78C,
            "TPolyMap.RayCast": 0x0060D59C
        },
    1: { # 1.7.1 to be populated later
            "GfxCreateTexture": 0x0050919C,
            "RenderInterface": 0x005BD628,
            "GfxDrawSprite": 0x00509974, # change to other overload
            "ifacebyte": b"\x40",
            "own_id": 0x00660800
        }
}