"""Upload the Tape 1 pilot to the owner's YouTube channel as Private."""

import argparse
import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def credentials(client_secret: Path, token_file: Path) -> Credentials:
    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
        creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    token_file.write_text(creds.to_json())
    return creds


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-secret", type=Path, required=True)
    parser.add_argument(
        "--video",
        type=Path,
        default=Path(__file__).resolve().parent / "pilot-tape1" / "Abe_Tabak_Tape_1.mp4",
    )
    parser.add_argument(
        "--token-file",
        type=Path,
        default=Path(__file__).resolve().parent / ".youtube-oauth-token.json",
    )
    args = parser.parse_args()

    youtube = build("youtube", "v3", credentials=credentials(args.client_secret, args.token_file))
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": "The Abe Tabak Tapes — Tape 1",
                "description": (
                    "Family oral-history recording with Abraham ‘Abe’ Tabak, Bella (Rita), "
                    "Nina, and Len. This private archival upload accompanies a timestamped, "
                    "annotated transcript under editorial review."
                ),
                "categoryId": "22",
                "defaultLanguage": "en",
                "tags": ["family oral history", "Abe Tabak", "Krasnobrod", "Yiddish"],
            },
            "status": {
                "privacyStatus": "private",
                "selfDeclaredMadeForKids": False,
            },
        },
        media_body=MediaFileUpload(
            str(args.video), mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True
        ),
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {status.progress() * 100:.1f}%", flush=True)

    video_id = response["id"]
    result = {
        "video_id": video_id,
        "watch_url": f"https://www.youtube.com/watch?v={video_id}",
        "studio_url": f"https://studio.youtube.com/video/{video_id}/edit",
        "privacy": "private",
    }
    output = args.video.with_name("youtube-upload.json")
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
