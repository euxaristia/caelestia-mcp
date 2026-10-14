# Copyright © 2026 euxaristia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Caelestia MCP Server.

Provides Model Context Protocol (MCP) tools for interacting with the
Caelestia shell (Quickshell) and Hyprland compositor.
"""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any, Literal
from mcp.server.mcpserver import MCPServer

# Initialize server
server = MCPServer(
    name="caelestia",
    version="1.0.0",
    description="Control and query the Caelestia shell (Quickshell) and Hyprland compositor.",
)

_ENV = dict(os.environ)
_LOCAL_LIB = os.path.expanduser("~/.local/lib")
if os.path.exists(_LOCAL_LIB):
    _ENV["LD_LIBRARY_PATH"] = f"{_LOCAL_LIB}:{_ENV.get('LD_LIBRARY_PATH', '')}".rstrip(":")


def _run_caelestia(*args: str) -> str:
    """Run a caelestia CLI command and return its trimmed stdout."""
    res = subprocess.run(
        ["caelestia", *args],
        capture_output=True,
        text=True,
        env=_ENV,
        check=True,
    )
    return res.stdout.strip()


def _run_hyprctl(*args: str) -> str:
    """Run a hyprctl command and return its trimmed stdout."""
    res = subprocess.run(
        ["hyprctl", *args],
        capture_output=True,
        text=True,
        env=_ENV,
        check=True,
    )
    return res.stdout.strip()


# ==============================================================================
# Notifications & UI Toasts
# ==============================================================================


@server.tool()
def caelestia_send_toast(
    title: str,
    message: str,
    level: Literal["info", "success", "warn", "error"] = "info",
    icon: str = "",
) -> str:
    """Send an on-screen toast popup notification through Caelestia shell.

    Args:
        title: Toast heading/title text.
        message: Body description of the notification.
        level: Notification level ('info', 'success', 'warn', 'error').
        icon: Optional Material Symbols icon name (e.g. 'check_circle', 'info', 'warning', 'error', 'terminal').
    """
    if not icon:
        icon_map = {
            "info": "info",
            "success": "check_circle",
            "warn": "warning",
            "error": "error",
        }
        icon = icon_map.get(level, "info")

    try:
        _run_caelestia("shell", "toaster", level, title, message, icon)
        return f"Toast sent ({level}): {title} - {message}"
    except Exception as e:
        return f"Error sending toast: {e}"


@server.tool()
def caelestia_set_dnd(enabled: bool) -> str:
    """Enable or disable Do Not Disturb (DND) mode for desktop notifications."""
    try:
        action = "enableDnd" if enabled else "disableDnd"
        _run_caelestia("shell", "notifs", action)
        return f"Do Not Disturb {'enabled' if enabled else 'disabled'}."
    except Exception as e:
        return f"Error setting DND: {e}"


@server.tool()
def caelestia_get_dnd() -> bool:
    """Check whether Do Not Disturb (DND) is currently active."""
    try:
        out = _run_caelestia("shell", "notifs", "isDndEnabled")
        return out.lower() == "true"
    except Exception:
        return False


# ==============================================================================
# Theming & Wallpaper
# ==============================================================================


@server.tool()
def caelestia_set_wallpaper(
    path: str = "",
    random: bool = False,
    directory: str = "",
) -> str:
    """Change the desktop wallpaper and automatically adapt system colors.

    Args:
        path: Path to an image file to set as wallpaper.
        random: If True, selects a random wallpaper instead.
        directory: Optional directory of wallpapers to pick from when random is True.
    """
    try:
        if random:
            cmd = ["wallpaper", "-r"]
            if directory:
                cmd.append(directory)
            _run_caelestia(*cmd)
            current = _run_caelestia("shell", "wallpaper", "get")
            return f"Switched to random wallpaper: {current}"
        elif path:
            expanded = os.path.expanduser(path)
            if not os.path.exists(expanded):
                return f"Error: Wallpaper file not found: {expanded}"
            _run_caelestia("wallpaper", "-f", expanded)
            return f"Wallpaper set to: {expanded}"
        else:
            return "Please provide either path or set random=True."
    except Exception as e:
        return f"Error changing wallpaper: {e}"


@server.tool()
def caelestia_get_wallpaper() -> str:
    """Get the absolute path to the currently active desktop wallpaper."""
    try:
        return _run_caelestia("shell", "wallpaper", "get")
    except Exception as e:
        return f"Error getting wallpaper: {e}"


@server.tool()
def caelestia_set_scheme(
    name: str = "",
    mode: Literal["dark", "light", ""] = "",
    variant: str = "",
) -> str:
    """Configure the Material You color scheme and dark/light mode.

    Args:
        name: Scheme palette name (e.g. 'dynamic', 'rosepine', 'caelestia', 'tokyonight', 'gruvbox', 'nord', 'catppuccin', 'dracula', 'onedark', 'everforest').
        mode: Either 'dark' or 'light'.
        variant: Palette variant ('tonalspot', 'vibrant', 'expressive', 'fidelity', 'fruitsalad', 'monochrome', 'neutral', 'rainbow', 'content').
    """
    args = ["scheme", "set"]
    if name:
        args.extend(["-n", name])
    if mode:
        args.extend(["-m", mode])
    if variant:
        args.extend(["-v", variant])

    if len(args) == 2:
        return "Please specify at least one of: name, mode ('dark'/'light'), or variant."

    try:
        _run_caelestia(*args)
        current = caelestia_get_scheme()
        return f"Scheme updated: {current}"
    except Exception as e:
        return f"Error setting scheme: {e}"


@server.tool()
def caelestia_get_scheme() -> dict[str, str]:
    """Get the current color scheme name, mode (dark/light), and variant."""
    try:
        out = _run_caelestia("scheme", "get", "-n", "-m", "-v")
        lines = [line.strip() for line in out.splitlines() if line.strip()]
        return {
            "name": lines[0] if len(lines) > 0 else "unknown",
            "mode": lines[1] if len(lines) > 1 else "unknown",
            "variant": lines[2] if len(lines) > 2 else "unknown",
        }
    except Exception as e:
        return {"error": str(e)}


# ==============================================================================
# Shell Drawers & Windows
# ==============================================================================


@server.tool()
def caelestia_open_settings() -> str:
    """Open the Caelestia Nexus desktop settings window."""
    try:
        _run_caelestia("shell", "nexus", "open")
        return "Opened Caelestia Nexus settings window."
    except Exception as e:
        return f"Error opening Nexus settings: {e}"


@server.tool()
def caelestia_toggle_drawer(
    drawer: Literal["launcher", "sidebar", "dashboard", "session", "utilities"],
) -> str:
    """Toggle a Caelestia shell drawer or popup panel.

    Args:
        drawer: Which drawer to toggle ('launcher', 'sidebar', 'dashboard', 'session', 'utilities').
    """
    try:
        _run_caelestia("shell", "drawers", "toggle", drawer)
        return f"Toggled drawer '{drawer}'."
    except Exception as e:
        return f"Error toggling drawer: {e}"


@server.tool()
def caelestia_lock_session() -> str:
    """Lock the desktop screen session."""
    try:
        _run_caelestia("shell", "lock", "lock")
        return "Desktop session locked."
    except Exception as e:
        return f"Error locking session: {e}"


@server.tool()
def caelestia_set_idle_inhibitor(enabled: bool) -> str:
    """Enable or disable the idle inhibitor to prevent the screen from sleeping/locking."""
    try:
        action = "enable" if enabled else "disable"
        _run_caelestia("shell", "idleInhibitor", action)
        return f"Idle inhibitor {'enabled' if enabled else 'disabled'}."
    except Exception as e:
        return f"Error setting idle inhibitor: {e}"


@server.tool()
def caelestia_get_idle_inhibitor() -> bool:
    """Check if the idle inhibitor is currently active."""
    try:
        out = _run_caelestia("shell", "idleInhibitor", "isEnabled")
        return out.lower() == "true"
    except Exception:
        return False


# ==============================================================================
# Media & Playback Controls
# ==============================================================================


@server.tool()
def caelestia_media_control(
    action: Literal["play", "pause", "playPause", "next", "previous", "stop"],
) -> str:
    """Control media playback (MPRIS / Spotify, Cider, Chrome, Firefox, etc.).

    Args:
        action: Media control action ('play', 'pause', 'playPause', 'next', 'previous', 'stop').
    """
    try:
        _run_caelestia("shell", "mpris", action)
        return f"Media action executed: {action}."
    except Exception as e:
        return f"Error controlling media: {e}"


@server.tool()
def caelestia_media_status() -> dict[str, str]:
    """Get the currently active media player, track title, artist, and status."""
    try:
        players = _run_caelestia("shell", "mpris", "list")
        if not players:
            return {"status": "no players found"}

        title = _run_caelestia("shell", "mpris", "getActive", "title")
        artist = _run_caelestia("shell", "mpris", "getActive", "artist")
        playback_status = _run_caelestia("shell", "mpris", "getActive", "playbackStatus")

        return {
            "title": title,
            "artist": artist,
            "playback_status": playback_status,
            "players": [p for p in players.splitlines() if p.strip()],
        }
    except Exception as e:
        return {"error": str(e)}


# ==============================================================================
# Hyprland Compositor Tools
# ==============================================================================


@server.tool()
def hyprland_get_active_window() -> dict[str, Any]:
    """Get metadata for the currently active/focused window in Hyprland."""
    try:
        data = _run_hyprctl("activewindow", "-j")
        return json.loads(data)
    except Exception as e:
        return {"error": str(e)}


@server.tool()
def hyprland_list_workspaces() -> list[dict[str, Any]]:
    """List all open Hyprland workspaces and their window counts."""
    try:
        data = _run_hyprctl("workspaces", "-j")
        return json.loads(data)
    except Exception as e:
        return [{"error": str(e)}]


@server.tool()
def hyprland_list_monitors() -> list[dict[str, Any]]:
    """List all connected displays/monitors, resolutions, refresh rates, and scales."""
    try:
        data = _run_hyprctl("monitors", "-j")
        return json.loads(data)
    except Exception as e:
        return [{"error": str(e)}]


@server.tool()
def hyprland_dispatch(command: str) -> str:
    """Execute a Hyprland dispatcher command (e.g. 'workspace 2', 'killactive', 'fullscreen 0').

    Args:
        command: Dispatcher command string (e.g. 'workspace 2', 'movetoworkspace 3', 'focuswindow <title>').
    """
    try:
        res = _run_hyprctl("dispatch", *command.split())
        return res if res else "Command dispatched successfully."
    except Exception as e:
        return f"Error executing dispatcher: {e}"


def main() -> None:
    """Run the MCP server over stdio transport."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
