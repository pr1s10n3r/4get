#!/usr/bin/env python3

import argparse
import concurrent
import concurrent.futures
import logging
import os
import re
import sys

import requests

VERSION = "1.0.0"


def get_board_thread(board: str, id: int) -> dict:
    resp = requests.get(f"https://a.4cdn.org/{board}/thread/{id}.json")
    if resp.status_code != 200:
        raise f"{resp.text}"
    return resp.json()


def save_thread_post(board: str, post: dict, output: str, keep_filename=False) -> None:
    post_tim = str(post.get("tim"))
    post_ext = post.get("ext")

    local_output_path = (
        os.path.join(output, post.get("filename") + post_ext)
        if keep_filename
        else os.path.join(output, post_tim + post_ext)
    )
    logging.debug(f"Downloading {post_tim + post_ext} into {local_output_path}")

    resp = requests.get(f"https://i.4cdn.org/{board}/{post_tim}{post_ext}")
    if resp.status_code != 200:
        post_no = post.get("no")
        logging.error(f"Could not download post no. {post_no}: {resp.text}")
        return

    with open(local_output_path, "wb") as file:
        file.write(resp.content)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="4get", description="4chan thread media downloader"
    )

    parser.add_argument("-t", "--thread", help="4chan thread url")
    parser.add_argument("--version", action="store_true", help="print version and exit")
    parser.add_argument(
        "-o", "--output", dest="output", default=".", help="output directory path"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="show debug information"
    )
    parser.add_argument(
        "--ignore-formats",
        default=[],
        dest="ignore_formats",
        help="comma separated values of formats to ignore",
    )
    parser.add_argument(
        "--keep-filename",
        action="store_true",
        dest="keep_filename",
        help="if set, if the media has a filename it will be used instead of 4chan timestamp",
    )

    args = parser.parse_args()

    logging.basicConfig(
        format="[{asctime} {levelname}] {message}",
        style="{",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    # Disable requests debug logging
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    if args.version:
        print(f"4get v{VERSION}")
        sys.exit(0)

    if not os.path.exists(args.output):
        logging.warning("Output directory does not exists, creating it")
        os.makedirs(args.output)

    expmatch = re.search(r"https://boards.4chan.org/(\w+)/thread/(\d+)", args.thread)
    if expmatch:
        board = expmatch.group(1)
        thread_id = expmatch.group(2)
    else:
        logging.fatal("Could not extract board and thread id from provided URL")
        sys.exit(1)

    thread = None
    try:
        thread = get_board_thread(board, thread_id)
    except Exception as e:
        logging.error(f"Could not get thread: {e}")
        sys.exit(1)

    ignored_formats = []
    if args.ignore_formats:
        ignored_formats = [
            fmt.strip().replace(".", "") for fmt in args.ignore_formats.strip().split(",")
        ]

    posts = [
        p
        for p in thread.get("posts")
        if "filename" in p and p.get("ext").replace(".", "") not in ignored_formats
    ]

    if not posts:
        logging.error("Thread does not have posts or no post match your criteria")
        sys.exit(1)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(
                save_thread_post, board, post, args.output, args.keep_filename
            ): post
            for post in posts
        }

        for future in concurrent.futures.as_completed(futures):
            try:
                rs = future.result()
            except Exception as e:
                logging.error(f"Post could not be downloaded: {e}")
