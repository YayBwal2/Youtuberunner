import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    YOUTUBE_CLIENT_SECRETS_FILE,
    YOUTUBE_TOKEN_FILE,
    YOUTUBE_PRIVACY_STATUS,
    YOUTUBE_CATEGORY_ID
)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_authenticated_service():
    """Authenticates using Google OAuth2 and returns the YouTube service resource."""
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    token_path = Path(YOUTUBE_TOKEN_FILE)
    secrets_path = Path(YOUTUBE_CLIENT_SECRETS_FILE)

    if not secrets_path.exists():
        print(f"\n[INFO] YouTube client secrets file '{secrets_path.name}' not found.")
        print("  → Skipping upload. Video is safely saved locally in outputs/.")
        print("  → To enable auto-upload: Google Cloud Console > APIs > Enable YouTube Data API v3 > OAuth 2.0 Client ID (Desktop) > download as 'client_secret.json'.\n")
        return None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_path, "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    privacy_status: Optional[str] = None,
    thumbnail_path: Optional[str] = None
) -> Optional[str]:
    """
    Uploads a video to YouTube with metadata and optional custom thumbnail.
    Returns the YouTube Video ID if successful, or None.
    """
    from googleapiclient.http import MediaFileUpload

    privacy = privacy_status or YOUTUBE_PRIVACY_STATUS
    print(f"\n[4/4] Uploading to YouTube (Mode: {privacy.upper()})...")

    service = get_authenticated_service()
    if not service:
        return None

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:20],
            "categoryId": YOUTUBE_CATEGORY_ID
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(
        video_path,
        chunksize=-1,
        resumable=True,
        mimetype="video/mp4"
    )

    request = service.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Uploading: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    video_url = f"https://youtu.be/{video_id}"
    print(f"  ✓ Successfully uploaded! Video ID: {video_id}")
    print(f"  ✓ URL: {video_url} ({privacy.upper()} mode)")

    # Upload custom thumbnail if provided
    if thumbnail_path and Path(thumbnail_path).exists():
        try:
            service.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/png")
            ).execute()
            print(f"  ✓ Custom thumbnail uploaded successfully!")
        except Exception as e:
            print(f"  [INFO] Channel thumbnail upload notice: {e}")

    return video_id


if __name__ == "__main__":
    print("YouTube uploader module loaded successfully.")
