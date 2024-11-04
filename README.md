# 4get

Multithreading 4chan media downloader

## Installation

Download to your local machine and install dependencies using a virtualenv.
Inside your local clone of 4get execute these commands:

```shell
# Create virtual environment
python -m venv .venv

# Linux/MacOS
source .venv/bin/activate
# Windows/Powershell
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

Then you can make `main.py` executable if you dont want to type `python` everytime:

```shell
chmod +x main.py
```

## Usage

```shell
usage: 4get [-h] [-t THREAD] [--version] [-o OUTPUT] [-v] [--ignore-formats IGNORE_FORMATS] [--keep-filename]

4chan thread media downloader

options:
  -h, --help            show this help message and exit
  -t THREAD, --thread THREAD
                        4chan thread url
  --version             print version and exit
  -o OUTPUT, --output OUTPUT
                        output directory path
  -v, --verbose         show debug information
  --ignore-formats IGNORE_FORMATS
                        comma separated values of formats to ignore
  --keep-filename       if set, if the media has a filename it will be used instead of 4chan timestamp
```

### Examples

1. Download a thread without certain media types.

```shell
python main.py --ignore-formats "webm,gif,png" -t https://boards.4chan.org/\<board\>/thread/\<thread id\>
```

2. Download media into especific output directory.

```shell
python main.py -o /path/to/directory -t https://boards.4chan.org/\<board\>/thread/\<thread id\>
```

3. Keep original filename instead of 4chan timestamp.

```shell
python main.py --keep-filename /path/to/directory -t https://boards.4chan.org/\<board\>/thread/\<thread id\>
```

## License

See [LICENSE](./LICENSE) file.