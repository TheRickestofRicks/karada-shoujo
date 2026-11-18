## characters.rpy — names and Character objects.
##
## ── RENAME HERE ──────────────────────────────────────────────────────────────
## Placeholder names. Change the strings and everything follows (dialogue tags,
## system prompts, sprite labels, menus).

## The four AI girls (LLM-driven), one per platform archetype:
define local_name     = "Yuzu"       # the Local option: runs on your own PC
define hikari_name    = "Hikari"     # the Companion-app girl
define chatbot_name   = "Sora"       # the general assistant Chatbot
define agent_name     = "Rei"        # the autonomous Agent

## Their platforms:
define local_platform     = "your old desktop (LM Studio, offline)"
define app_name           = "Tsunagari"   # commercial companion app
define chatbot_platform   = "Askwell"     # big general-purpose chatbot service
define agent_platform     = "Relay"       # agent platform that does tasks for you

## Humans:
define mio_name    = "Mio"        # girl with a crush (scripted only)
define daichi_name = "Daichi"     # the friend
## Tuesday:
define kurosawa_name = "Kurosawa-sensei"  # lecturer, openly anti-AI
define ran_name      = "Ran"              # classmate with an uncensored local model
define ran_model     = "MUGEN"            # what Ran calls her model ("no limits")
define kenta_name    = "Kenta"            # Daichi's friend from the futsal club

default player_name = "Haru"

## Display names per platform slot. They start as the names above; after a
## persona migration the destination slot takes the migrated girl's name.
default dn_local     = local_name
default dn_companion = hikari_name
default dn_chatbot   = chatbot_name
default dn_agent     = agent_name

## ─────────────────────────────────────────────────────────────────────────────

define g_local     = Character("[dn_local]",     color="#c9e4a8")
define g_companion = Character("[dn_companion]", color="#9fd6ff")
define g_chatbot   = Character("[dn_chatbot]",   color="#e0c3ff")
define g_agent     = Character("[dn_agent]",     color="#ffb27a")

define mi  = Character("[mio_name]",    color="#ffb3c7")
define d   = Character("[daichi_name]", color="#ffd27a")
define ks  = Character("[kurosawa_name]", color="#c8d0dc")
define ra  = Character("[ran_name]",      color="#c9a8ff")
define mu  = Character("[ran_model]",     color="#ff6b8b", what_color="#ffd0da")
define ke  = Character("[kenta_name]",    color="#9be0b0")
define p   = Character("[player_name]", color="#d8d8d8")
define app = Character("System",        color="#a8ffcf", what_italic=True)
define n   = Character(None)

init python:
    ## Girl registry. id -> name variable, Character variable, platform variable,
    ## sprite tag. Everything else (prompts, memory files, config) keys off id.
    GIRL_IDS = ["local", "companion", "chatbot", "agent"]
    GIRL_INFO = {
        "local":     dict(name_var="local_name",   char="g_local",     platform_var="local_platform",   sprite="girl_local",     kind="Local"),
        "companion": dict(name_var="hikari_name",  char="g_companion", platform_var="app_name",         sprite="girl_companion", kind="Companion app"),
        "chatbot":   dict(name_var="chatbot_name", char="g_chatbot",   platform_var="chatbot_platform", sprite="girl_chatbot",   kind="Chatbot"),
        "agent":     dict(name_var="agent_name",   char="g_agent",     platform_var="agent_platform",   sprite="girl_agent",     kind="Agent"),
    }

    def gname(gid):
        """Current display name of whoever lives in this platform slot."""
        return getattr(store, "dn_" + gid)

    def gdefault_name(gid):
        """The slot's original (non-migrated) persona name."""
        return getattr(store, GIRL_INFO[gid]["name_var"])

    def gplatform(gid):
        return getattr(store, GIRL_INFO[gid]["platform_var"])

    def gchar(gid):
        return getattr(store, GIRL_INFO[gid]["char"])
