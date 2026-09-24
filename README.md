# SetLAB

A small Mac app for saving audio from YouTube (and SoundCloud, and [many other sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)) as MP3s. Paste a link, pick a folder, hit **Download**. Single songs and whole playlists both work.

Under the hood it's a PyQt5 window around [yt-dlp](https://github.com/yt-dlp/yt-dlp) and ffmpeg.

> Only download audio you have the right to download.

---

## Setup (one time)

You need a Mac and [Homebrew](https://brew.sh). If you don't have Homebrew, install it first by pasting the command from brew.sh into Terminal.

Then, in Terminal:

```bash
git clone https://github.com/kyivey/setLAB.git
cd setLAB
./setup.sh --build
```

This installs everything SetLAB needs and builds the app. It takes a few minutes the first time. When it's done you'll have **`dist/SetLAB.app`**. Drag it into your Applications folder (or anywhere you like) and open it like any other app.

<details>
<summary>What <code>setup.sh</code> installs</summary>

| What | From | Why |
|---|---|---|
| Python 3.13 | Homebrew (`Brewfile`) | Runs the app and yt-dlp |
| ffmpeg | Homebrew (`Brewfile`) | Converts the audio to MP3 |
| Deno | Homebrew (`Brewfile`) | yt-dlp needs a JavaScript runtime to download from YouTube |
| PyQt5, PyInstaller | pip (`requirements.txt`), into a local `.venv` folder | The app window, and building `SetLAB.app` |

It also updates the bundled `yt-dlp` to the latest version.

To do it by hand instead:

```bash
brew bundle
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python yt-dlp -U
.venv/bin/pyinstaller SetLAB.spec --noconfirm
```
</details>

## Using SetLAB

1. Copy a YouTube (or SoundCloud) link, either a single video or a playlist.
2. Paste it into the box at the top.
3. Click **Choose Folder** to pick where the MP3s go. The default is your **Downloads** folder.
4. Click **Download**. Progress shows in the log below, and a message pops up when it's finished.
5. If something gets stuck, click **Stop** to cancel. You can start a new download straight away.

MP3s are saved at the best available quality and named after the video title.

**Run without building the app:** `.venv/bin/python SetLAB.py`

**Use it from the command line:** `./getSong.sh "<link>" ~/Music`

## Keeping it working

YouTube changes often, and old versions of yt-dlp stop working. If downloads start failing, update yt-dlp and rebuild:

```bash
cd setLAB
git pull            # get any fixes to SetLAB itself
./setup.sh --build  # updates yt-dlp and rebuilds the app
```

Then replace your old copy of `SetLAB.app` with the new one from `dist/`.

## Troubleshooting

Every download writes a detailed log to **`~/Library/Logs/SetLAB.log`**. That's the first place to look, and the file to send if you ask for help. To open it: in Finder press ⌘⇧G, then paste `~/Library/Logs/SetLAB.log`.

| Problem | Fix |
|---|---|
| "ffmpeg not found" | `brew install ffmpeg` |
| "No JavaScript runtime found", or YouTube errors about a "challenge" or "signature" | `brew install deno` |
| Download fails right away, or YouTube says the video is unavailable | Update yt-dlp: `./setup.sh --build` |
| Stuck on "Downloading webpage" | Already handled (SetLAB forces IPv4). If it still happens, try a different network, or turn off any VPN. |
| "SetLAB can't be opened" when you open the app | Right-click the app, choose **Open**, then **Open** again. You only need to do this once. |
| Some playlist songs fail | Private, deleted, or region-locked videos can't be downloaded. The rest of the playlist still downloads. |

## Project files

| File | What it is |
|---|---|
| `SetLAB.py` | The app window |
| `getSong.sh` | The download script the app runs (also works on its own) |
| `yt-dlp` | Bundled copy of yt-dlp |
| `SetLAB.spec` | PyInstaller recipe for building `SetLAB.app` |
| `setup.sh` | One-step setup and build |
| `Brewfile` / `requirements.txt` | System and Python dependencies |

## License

MIT, see [LICENSE](LICENSE).
