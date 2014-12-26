#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: set.py
# by Arzaroth Lekva
# arzaroth@arzaroth.com
#

def set_currency(xml_handle, args):
    for currency_id in args['<currency_id>']:
        for typ in xml_handle.currencies.values():
            for val in typ.values():
                if currency_id == val.name:
                    try:
                        val.value = args['<value>']
                    except ValueError as e:
                        print(str(e))

def _process_set_pony(xml_handle, pony, args):
    if args['level']:
        if args['up']:
            pony.level_up()
        elif args['down']:
            pony.level_down()
        else:
            pony.level = args['<value>']
    elif args['shards']:
        if args['up']:
            pony.shard_up()
        elif args['down']:
            pony.shard_down()
        else:
            pony.shards = args['<value>']
    elif args['next_game']:
        try:
            pony.next_game = Pony.GameTypes.map[args['<value>']]
        except KeyError:
            raise ValueError("Invalid game type")
    elif args['reset_game_timer']:
        pony.reset_game_timer()

def set_ponies(xml_handle, args):
    try:
        for pony in xml_handle.ponies.values():
            _process_set_pony(xml_handle, pony, args)
    except Exception as e:
        print(str(e))

def set_pony(xml_handle, args):
    try:
        for pony_id in args['<pony_id>']:
            if pony_id in xml_handle.ponies:
                _process_set_pony(xml_handle, xml_handle.ponies[pony_id], args)
    except Exception as e:
        print(str(e))

def _process_set_zone(xml_handle, zone, args):
    if args['clearables']:
        zone.clear_clearable_items()
    elif args['foes']:
        zone.clear_foes()
    else:
        zone.clear_all()

def set_zones(xml_handle, args):
    for zone in xml_handle.zones.values():
        _process_set_zone(xml_handle, zone, args)

def set_zone(xml_handle, args):
    for zone_id in args['<zone_id>']:
        if zone_id in xml_handle.zones:
            _process_set_zone(xml_handle, xml_handle.zones[zone_id], args)