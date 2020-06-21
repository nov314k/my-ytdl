import datetime
import os
import json
import subprocess
import urllib.request


def print_command_history():
    print("Command history:", end="")
    for command in command_history:
        print(" " + command[1], end="")
    print(".")


def update_ytdl():
    os.system(f"{ytdl} --update")


def list_formats():
    os.system(f'{ytdl} --list-formats {video["url"]}')


def list_subtitles():
    os.system(f'{ytdl} --list-subs {video["url"]}')


def runme(command):
    cmd = " ".join([aux_cmd for aux_cmd in command])
    os.system(f"{cmd}")


def runme_sp(command):
    runme_output = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    stdout, stderr = runme_output.communicate()
    print("STDERR: ", stderr)
    response = input("Print STDOUT? [y = yes]: ")
    if response == "y":
        print("STDOUT: ", stdout)


def download_aux_files():
    command = [
        ytdl,
        "--rm-cache-dir",
        "--no-continue",
        "--no-overwrites",
        "--write-description",
        "--write-info-json",
        "--write-annotations",
        "--write-all-thumbnails",
        "--skip-download",
        "--output",
        f'"{video["folder"]}/{video["folder"]}-%(title)s-%(id)s.%(ext)s"',
        video["url"],
    ]
    runme(command)
    command = [
        ytdl,
        "--rm-cache-dir",
        "--no-continue",
        "--no-overwrites",
        "--write-info-json",
        "--write-thumbnail",
        "--skip-download",
        "--output",
        f'"{video["folder"]}/{video["folder"]}"',
        video["url"],
    ]
    runme(command)
    with open(f'{video["folder"]}/{video["folder"]}.info.json', "r") as opf:
        info_json = json.load(opf)
    with open(f'{video["folder"]}/{video["folder"]}.info.json', "w") as opf:
        json.dump(info_json, opf, indent=2)
    command = [
        ytdl,
        "--list-formats",
        "--skip-download",
        video["url"],
        ">",
        f'{video["folder"]}/{video["folder"]}-formats.txt',
    ]
    runme(command)


def download_video(ask_user=True, download_format=""):
    if ask_user:
        download_format = input("Enter download format: ")
    download_format_list = download_format.split(" ")
    for df in download_format_list:
        command_history.append(["download_video", df])
        command = [
            ytdl,
            "--rm-cache-dir",
            "--no-continue",
            "--no-overwrites",
            "--embed-thumbnail",
            "--add-metadata",
            "--ffmpeg-location",
            ffmpeg,
            "--format",
            df,
            "--output",
            f'"{video["folder"]}/{video["folder"]}-{video["shorttitle"]}-%(format_id)s.%(ext)s"',
            video["url"],
        ]
        runme(command)


def extract_mp3(ask_user=True, download_format=""):
    if ask_user:
        download_format = input("Enter download format: ")
    download_format_list = download_format.split(" ")
    for df in download_format_list:
        command_history.append(["extract_mp3", df])
        filename = f'{video["folder"]}/{video["folder"]}-{video["shorttitle"]}'
        command = [
            ytdl,
            "--rm-cache-dir",
            "--no-continue",
            "--no-overwrites",
            "--keep-video",
            "--extract-audio",
            "--audio-format",
            "mp3",
            "--audio-quality",
            "9",
            "--embed-thumbnail",
            "--add-metadata",
            "--ffmpeg-location",
            ffmpeg,
            "--format",
            f"{df}",
            "--output",
            f'"{filename}-%(format_id)s.aux"',
            video["url"],
        ]
        runme(command)
        if video["talk_start"] == "" or video["talk_end"] == "":
            command = [
                "copy",
                f"{filename}-???.mp3",
                f"{filename}.mp3",
            ]
        else:
            talk_start = datetime.datetime.strptime(video["talk_start"], "%H:%M:%S.%f")
            talk_end = datetime.datetime.strptime(video["talk_end"], "%H:%M:%S.%f")
            duration = talk_end - talk_start
            command = [
                ffmpeg,
                "-ss",
                video["talk_start"],
                "-i",
                f"{filename}-???.mp3",
                "-c",
                "copy",
                "-t",
                str(duration),
                f"{filename}.mp3",
            ]
        runme(command)


def download_subtitles():
    command = [
        ytdl,
        "--rm-cache-dir",
        "--no-continue",
        "--no-overwrites",
        "--write-auto-sub",
        "--sub-format",
        "vtt",
        "--sub-lang",
        "en",
        "--no-post-overwrites",
        "--convert-subs",
        "srt",
        "--skip-download",
        "--output",
        f'{video["folder"]}/{video["folder"]}-{video["shorttitle"]}',
        video["url"],
    ]
    runme(command)


def download_the_lot():
    download_aux_files()
    download_subtitles()
    download_video(ask_user=False, download_format="best worst")
    extract_mp3(ask_user=False, download_format="bestaudio")
    embed_thumbnail()


def download_the_lot_for_all():
    global video
    for video_idx in range(first_idx, last_idx + 1):
        video = {
            "folder": urls[video_idx][0],
            "url": urls[video_idx][1],
            "shorttitle": urls[video_idx][4],
            "talk_start": urls[video_idx][2],
            "talk_end": urls[video_idx][3],
        }
        download_the_lot()
    exit()


def embed_thumbnail():
    address = f'https://i.ytimg.com/vi/{video["url"][32:]}/hqdefault.jpg'
    thumbnail_file = f'{video["folder"]}/{video["folder"]}-thumbnail.jpg'
    mp3_file = f'{video["folder"]}/{video["folder"]}-{video["shorttitle"]}.mp3'
    output_mp3_file = (
        f'{video["folder"]}/{video["folder"]}-{video["shorttitle"]}-tn.mp3'
    )
    urllib.request.urlretrieve(address, thumbnail_file)
    command = [
        ffmpeg,
        "-i",
        mp3_file,
        "-i",
        thumbnail_file,
        "-map",
        "0:0",
        "-map",
        "1:0",
        "-c",
        "copy",
        "-id3v2_version",
        "3",
        output_mp3_file,
    ]
    runme(command)


def exit_program():
    pass


if __name__ == "__main__":
    with open("settings.json", "r") as opf:
        settings = json.load(opf)

    ffmpeg = settings["ffmpeg_path"]
    ytdl = settings["youtube_dl_path"]
    urls = settings["number_url_shorttitle"]
    first_idx = int(settings["first_idx"])
    last_idx = int(settings["last_idx"])

    menu = """
    1   Update youtube-dl
    2   List formats
    3   List subtitles
    4   Download auxiliary files
    5   Download video file (separate multiple format codes by space)
    6   Download and extract mp3
    7   Download subtitles
    8   Download everything ("the lot"): best, worst, bestaudio, cut mp3 (+tn)
    9   Embed jpg thumbnail image
    a   Download everything ("the lot") for all videos
    0   Next video / Exit program after last video
    """

    commands = {
        "1": update_ytdl,
        "2": list_formats,
        "3": list_subtitles,
        "4": download_aux_files,
        "5": download_video,
        "6": extract_mp3,
        "7": download_subtitles,
        "8": download_the_lot,
        "9": embed_thumbnail,
        "a": download_the_lot_for_all,
        "0": exit_program,
    }

    video = dict()
    command_history = []
    for video_idx in range(first_idx, last_idx + 1):
        video = {
            "folder": urls[video_idx][0],
            "url": urls[video_idx][1],
            "shorttitle": urls[video_idx][4],
            "talk_start": urls[video_idx][2],
            "talk_end": urls[video_idx][3],
        }
        command = ""
        while command != "0":
            print("*******")
            print(f"{video['folder']}: {video['shorttitle']}")
            print(menu)
            print_command_history()
            command = input("Enter command: ")
            command_history.append(["main", command])
            if command in commands.keys():
                commands[command]()
            else:
                print("Entered command is not available")

    print("Bye!")
