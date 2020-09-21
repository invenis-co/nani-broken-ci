import argparse
import logging
import pathlib
import time

import gitlab
import vlc


path = pathlib.Path(__file__).parent.absolute()

FAILED = "failed"
DEFAULT_LOOP_SECONDS = 60
DEFAULT_FILE_NAME = "nani.mp3"
p = vlc.MediaPlayer(f"/{path}/{DEFAULT_FILE_NAME}")


def play_nani():
    p.play()
    time.sleep(0.1)
    while p.is_playing():
        time.sleep(0.1)
    p.stop()


def get_all_projects_status(projects):
    failed = {}
    for project in projects:
        try:
            pipelines = project.pipelines.list()
            if pipelines:
                status = pipelines[0].status  # Pipelines are ordered by id
                failed[project] = status
        except (gitlab.exceptions.GitlabHttpError, gitlab.exceptions.GitlabListError):
            pass
    return failed


def check_new_failed(old_status, new_status):
    for project, status in new_status.items():
        if status == FAILED and old_status[project] != FAILED:
            logging.info(f"{project.name} has failed")
            play_nani()


def loop(projects, seconds):
    logging.info("Get initial values")
    old_status = get_all_projects_status(projects)
    while True:
        time.sleep(seconds)
        logging.info("Get new values")
        new_status = get_all_projects_status(projects)
        check_new_failed(old_status, new_status)
        old_status = new_status


def get_projects(url, token, groups, projects):
    gl = gitlab.Gitlab(url, private_token=token)
    all_projects = []
    if groups:
        for group_name in groups:
            group_id = gl.groups.list(search=group_name)[0].id
            all_projects.extend(gl.projects.list(group_id=group_id))
    if projects:
        for project_name in projects:
            all_projects.append(gl.projects.list(name=project_name)[0])
    return all_projects


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Gitlab url (https://example.com)")
    parser.add_argument("-g", "--groups", nargs="*", help="Project group names")
    parser.add_argument("-p", "--projects", nargs="*", help="Projects names")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show some logs")
    parser.add_argument(
        "-s",
        "--seconds",
        default=DEFAULT_LOOP_SECONDS,
        type=int,
        help="Seconds between 2 checks",
    )
    parser.add_argument(
        "-t", "--test", action="store_true", help="Test connection and sound"
    )

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    token = open("token.txt").read().strip()

    all_projects = get_projects(args.url, token, args.groups, args.projects)
    logging.info(f"Found {len(all_projects)} projects")

    if args.test:
        play_nani()
    else:
        loop(all_projects, args.seconds)


if __name__ == "__main__":
    main()
