# Caelestia MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server allowing AI models (Claude Desktop, Antigravity, Cursor, etc.) to control and inspect the [Caelestia](https://github.com/caelestia-dots/shell) Linux desktop shell and the [Hyprland](https://hyprland.org) Wayland compositor.

## Features

- **Toasts & Notifications**: Display styled on-screen toast popups (`info`, `success`, `warn`, `error`) and toggle Do Not Disturb.
- **Theming & Wallpaper**: Switch wallpapers (specific or random) and adjust Material You color schemes, dark/light mode, and palette variants.
- **Shell Controls**: Open Nexus settings, toggle shell drawers (`launcher`, `sidebar`, `dashboard`, `session`), lock screen, and toggle the idle inhibitor.
- **Media Controls**: Control MPRIS playback (play, pause, next, previous) and query active tracks and artists.
- **Hyprland Compositor Tools**: Inspect active windows, list workspaces and monitors, and dispatch compositor commands.

## Installation & Running

Installed in the local virtual environment:

```bash
cd /home/euxaristia/Projects/caelestia-mcp
./.venv/bin/pip install -e .
```

Executable binary path:
`/home/euxaristia/Projects/caelestia-mcp/.venv/bin/caelestia-mcp`

## Configuration in Claude Desktop

Add the following to `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "caelestia": {
      "command": "/home/euxaristia/source/caelestia-mcp/.venv/bin/caelestia-mcp"
    }
  }
}
```
