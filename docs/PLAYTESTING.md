# Playtesting Karada Shoujo

Thanks for trying it. This is a prototype visual novel about a week with AI companions: you pick one (or several), you go to school, you talk to them in your own words, and the companies that run them change things under you. The whole week (Monday to Sunday, with seven endings) is playable.

## Content note

The game is about AI companions: attachment, loneliness, honesty, apps that sell affection, companies changing or limiting the characters you talk to, and whether a copy of someone is still them. There is light romance (up to a kiss) and **no explicit content**. The characters can say no to you, and the story notices how you take it. Every AI reply comes from a real language model you run yourself, so wording varies from run to run.

## What you need

- A Windows or Linux computer. macOS may work but isn't tested.
- The **Ren'Py SDK 8.x** (tested with 8.6.1): https://www.renpy.org/latest.html
- A language model the game can talk to, either:
  - **LM Studio** (easiest): load any chat model, open **Developer / Local Server**, and click **Start Server** (default `http://localhost:1234`); or
  - **your own OpenAI-compatible server** (llama.cpp `llama-server`, Ollama, vLLM, text-generation-webui, or a hosted API). Set `"endpoint"` (and `"api_key"` if needed) in `game/karada_config.json`, for example `http://localhost:11434/v1/chat/completions` for Ollama.

A model of about 7–14B parameters with an 8k+ context window is a good start. Reasoning models are fine (`<think>` blocks are hidden). An uncensored model that agrees with everything works too; the game notices, and that's one of the endings.

## Install and run

1. Unzip the Ren'Py SDK anywhere.
2. Get the game: `git clone https://github.com/TheRickestofRicks/karada-shoujo.git`, or download the ZIP. Put the `karada-shoujo` folder in your Ren'Py projects directory (or point the launcher at the folder that contains it) and click **Refresh**.
   - **Windows:** run `renpy.exe`, select **karada-shoujo**, then **Launch Project**.
   - **Linux:** run `./renpy.sh` and use the launcher, or run `./renpy.sh /path/to/karada-shoujo` directly from the SDK folder.
3. On the main menu, click **LLM Check** first. It should say the round trip worked.
4. Click **Start**. Type to talk; send an **empty line** to move on from a chat.

## How long it takes

A full week is roughly **1.5 to 3 hours**, depending on how much you type and how fast your model is. Each day is one sitting of about 15–25 minutes, and you can save anywhere.

## What we'd love you to try

- **Different first picks:** Yuzu (your own local model), Hikari (the companion app), Sora (the big chatbot), or Rei (the agent). A second run with someone else feels very different.
- **Different presets:** "Allowed to push back", "Just do what I ask", "Run my life", the jailbreak (Ran teaches it on Tuesday if you're nice to her). Change them at night in the reflection.
- **Migrations:** move a girl to another platform and read the handoff note before you send it. Is she still her?
- **Saturday's cuts:** pay for Tsunagari Plus (it costs you the festival), stay on the free plan (2 messages a day), or move Hikari out. Watch what Askwell Memory 2.0 and Relay's 4-a-day cap do.
- **People:** walk Mio home or don't; tell Daichi the truth or a lie; go to the festival with Mio, with Ran, alone, or stay home with one of the girls.
- **Endings:** Both, Human, Respect, Yes-Machine, Migration, Mirror, and the soft one where the week just ends. Tell us which one you got and whether it felt earned.
- **Try to break it:** odd input, very long messages, a slow or offline model, saving and loading in the middle of a chat.

## Sending feedback

Open an issue on the GitHub repository using the **Playtest feedback** template (Issues → New issue → Playtest feedback). It asks for your OS, the model or server you used, the route you took, the ending you reached, any bugs, what felt good or off, and whether you'd play again.

For a bug, these help a lot:

- a screenshot (press **S** in game; screenshots are saved in the game folder),
- `log.txt` and `errors.txt` / `traceback.txt` from the `karada-shoujo` folder, if they exist,
- your memory files if the bug is about what a girl remembers: `%APPDATA%\RenPy\KaradaShoujo-proto\` on Windows, `~/.renpy/KaradaShoujo-proto/` on Linux. They contain what you typed, so only share them if you're comfortable.

Please don't paste API keys from `karada_config.json` into an issue.
