import requests
import json
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()

API_key = os.getenv("API_KEY")
Channel_name = os.getenv("CHANNEL_HANDLE")


def get_playlist_id():
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={Channel_name}&key={API_key}"

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        print(json.dumps(data, indent=4))

        channel_items = data["items"][0]
        channel_playlist_id = channel_items["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]
        print(channel_playlist_id)

        return channel_playlist_id

    except requests.exceptions.RequestException as e:
        raise e


def get_video_ids(playlist_id):
    try:
        video_ids = []
        page_token = None
        base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId={playlist_id}&key={API_key}"

        while True:
            url = base_url  # FIX 1: fresh URL every loop
            if page_token:
                url += f"&pageToken={page_token}"

            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            # print(json.dumps(data, indent=4))

            for item in data["items"]:
                video_id = item["contentDetails"]["videoId"]
                video_ids.append(video_id)

            page_token = data.get("nextPageToken")
            if not page_token:
                break

        return video_ids  # FIX 2: give the list back

    except requests.exceptions.RequestException as e:
        raise e


def extract_video_data(video_ids):
    try:
        video_data = []

        def batch_video_ids(video_ids, batch_size=50):
            for i in range(0, len(video_ids), batch_size):
                yield video_ids[i : i + batch_size]

        for batch in batch_video_ids(video_ids):
            ids = ",".join(batch)
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={ids}&key={API_key}"

            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            # print(json.dumps(data, indent=4))

            for item in data["items"]:
                video_info = {
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "published_at": item["snippet"]["publishedAt"],
                    "view_count": item["statistics"].get("viewCount", 0),
                    "like_count": item["statistics"].get("likeCount", 0),
                    "comment_count": item["statistics"].get("commentCount", 0),
                }
                video_data.append(video_info)

        return video_data

    except requests.exceptions.RequestException as e:
        raise e


def save_to_json(extracted_data):
    os.makedirs("data", exist_ok=True)
    file_path = f"data/YT_data_{date.today()}.json"

    with open(file_path, "w", encoding="utf-8") as json_outfile:
        json.dump(extracted_data, json_outfile, indent=4, ensure_ascii=False)

    print(f"Saved {len(extracted_data)} videos to {file_path}")


if __name__ == "__main__":i
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    video_data = extract_video_data(video_ids)
    save_to_json(video_data)
