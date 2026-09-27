# SPDX-License-Identifier: GPL-3.0-only
# Copyright 2023 Marek Kraus <gamelaster@outlook.com>

# Updated for Flatpak support by Malivil

from gi.repository import GLib, Gio

bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

def emit_launcher_entry_update_signal(path, params):
    bus.emit_signal(
        None,  # sender
        path,  # object path
        "com.canonical.Unity.LauncherEntry",  # interface name
        "Update",  # signal name
        params,  # parameters
    )


def on_launcher_entry_update_signal_handler(*args):
    (app_uri, props) = args[5].unpack()

    # Redirect discord to the proper place so the taskbar icon shows notification badges (for pings and DMs at least)
    if app_uri == "application://discord":
        # Build out the parameters list manually to fit in GLib's JSON-like structure with limited typing
        paramParts = []
        for prop in props:
            propStr = "'{}': <".format(prop)
            propVal = props[prop]
            # Numbers seem to be the only type that is actually typed and they are all int64 or double
            if type(propVal) == int:
                propStr += "int64 "
            elif type(propVal) == float:
                propStr += "double "
            # De-python the boolean strings
            elif type(propVal) == bool:
                propVal = str(propVal).lower()
            propStr += "{}>".format(propVal)
            paramParts.append(propStr)
        # Join them all together, comma-delimited
        paramStr = "{{{}}}".format(", ".join(paramParts))
        params = GLib.Variant.parse(
            None,
            "('com.discordapp.Discord.desktop', {})".format(paramStr),
        )
        # Send the updated params to the same path
        emit_launcher_entry_update_signal(args[2], params)


bus.signal_subscribe(
    None,
    "com.canonical.Unity.LauncherEntry",
    None,
    None,
    None,
    Gio.DBusSignalFlags.NONE,
    on_launcher_entry_update_signal_handler,
)

mainloop = GLib.MainLoop()
mainloop.run()
