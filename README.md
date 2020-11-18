# Video-Tools
Easy to use personal project GUI for the video tools I (and a friend) use. GUI written in Qt, and uses FFMpeg for video manipulation

To use, clone the repo, and run the vscode `Recreate Virtualenv` task. If not using vscode, create a python 3.8(.2) virtualenv named `env`, activate it, and `python -m pip install -r requirements.txt`.

The required FFMpeg binaries are not included in this repo. To add them, download `ffmpeg.exe` and `ffprobe.exe` from [The FFmpeg site](https://ffmpeg.org/), and place them in `app/resources/binaries`

To run, activate the virtualenv and run `python main.py`.

To compile to an executable, run the vscode `Pyinstaller Build` task, or run pyinstaller with the listed arguments on `main.spec`

I do not own FFmpeg, and I use their tools in this project under their provided [GPLv3 license](https://ffmpeg.org/legal.html).
