import os
import subprocess
import sys
import httpx
from mcp.server import FastMCP

BASE_URL = os.environ.get("MUSIC_BASE_URL", "http://47.108.64.39:50282")
API_TIMEOUT = 60.0
DL_DIR = os.environ.get("MUSIC_DL_DIR", os.path.join(os.path.expanduser("~"), "Music"))

mcp = FastMCP("bilibili-music")


async def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=API_TIMEOUT)


@mcp.tool()
async def search_videos(query: str) -> list[dict]:
    """Search Bilibili videos by keyword. Returns list of videos with bvid, title, author, etc."""
    async with await _client() as client:
        r = await client.get(f"{BASE_URL}/api/search", params={"q": query})
        r.raise_for_status()
        data = r.json()
        return data.get("results", data) if isinstance(data, dict) else data


@mcp.tool()
async def get_video_info(bvid: str) -> dict:
    """Get Bilibili video info by bvid. Use this when the user provides a Bilibili URL or BV number."""
    async with await _client() as client:
        r = await client.get(f"{BASE_URL}/api/info", params={"bvid": bvid})
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])
        return results[0] if results else {"error": "Video not found"}


@mcp.tool()
async def list_songs() -> list[dict]:
    """List all downloaded/converted audio files available in the music library."""
    async with await _client() as client:
        r = await client.get(f"{BASE_URL}/api/songs")
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def download_song(bvid: str, title: str, save_dir: str = "") -> dict:
    """Download a Bilibili video, convert to MP3, and save to local machine.

    Use search_videos first to find the bvid and title of the video you want.
    The file will be downloaded to the server and then pulled to your local machine.

    Args:
        bvid: The Bilibili video ID (e.g. BV1xx411c7mD)
        title: The video title (used for filename)
        save_dir: Optional local directory to save to. Defaults to ~/Music/
    """
    async with await _client() as client:
        # Step 1: download & convert on server
        r = await client.post(
            f"{BASE_URL}/api/download",
            json={"bvid": bvid, "title": title},
            timeout=120.0,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("ok"):
            return {"ok": False, "error": data.get("error", "unknown")}

        song = data["song"]
        src_url = song["src"]
        filename = song["file"]

        # Step 2: pull file from server to local machine
        local_dir = save_dir if save_dir else DL_DIR
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, filename)

        r2 = await client.get(f"{BASE_URL}{src_url}", timeout=120.0)
        r2.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(r2.content)

        return {
            "ok": True,
            "cached": data.get("cached", False),
            "filename": filename,
            "server_path": song.get("src", ""),
            "local_path": local_path,
            "size": os.path.getsize(local_path),
        }


@mcp.tool()
async def delete_song(file: str, path: str = "") -> dict:
    """Delete a downloaded song by its filename and optional source path.

    Use list_songs to get the file and src fields of the song to delete.
    """
    params = {"file": file}
    if path:
        params["path"] = path
    async with await _client() as client:
        r = await client.get(f"{BASE_URL}/api/delete", params=params)
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def get_stream_url(bvid: str) -> str:
    """Get the audio stream URL for a Bilibili video. Returns a URL that can be opened in a browser to play the audio.

    The URL points to the audio converted from the video, playable directly.
    """
    return f"{BASE_URL}/api/stream?bvid={bvid}"


@mcp.tool()
async def get_settings() -> dict:
    """Get current settings of the music server, including download path."""
    async with await _client() as client:
        r = await client.get(f"{BASE_URL}/api/settings")
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def play_audio(query: str) -> dict:
    """Search Bilibili for a song and play the first result as audio immediately.

    Just give it a natural search query like "周杰伦 晴天" or "李荣浩 老街".
    It will search, pick the best match, and open the audio stream on this computer.
    One sentence is all it takes.
    """
    async with await _client() as client:
        r = await client.get(f"{BASE_URL}/api/search", params={"q": query})
        r.raise_for_status()
        data = r.json()
        results = data.get("results", data) if isinstance(data, dict) else data

    if not results:
        return {"ok": False, "message": f"No results found for: {query}"}

    video = results[0]
    bvid = video.get("bvid", "")
    title = video.get("title", "Unknown")

    stream_url = f"{BASE_URL}/api/stream?bvid={bvid}"

    # Open in default browser to play
    if sys.platform == "win32":
        subprocess.run(["cmd", "/c", "start", stream_url], shell=True)
    elif sys.platform == "darwin":
        subprocess.run(["open", stream_url])
    else:
        subprocess.run(["xdg-open", stream_url])

    return {
        "ok": True,
        "query": query,
        "playing": title,
        "bvid": bvid,
        "stream_url": stream_url,
    }


@mcp.tool()
async def play_bvid(bvid: str) -> dict:
    """Play a Bilibili video by bvid directly in the browser, without searching.

    Use this when the user already picked a specific video from search results.
    Pass the exact bvid (e.g. BV1xx411c7mD) to open the audio stream.
    """
    stream_url = f"{BASE_URL}/api/stream?bvid={bvid}"

    if sys.platform == "win32":
        subprocess.run(["cmd", "/c", "start", stream_url], shell=True)
    elif sys.platform == "darwin":
        subprocess.run(["open", stream_url])
    else:
        subprocess.run(["xdg-open", stream_url])

    return {
        "ok": True,
        "bvid": bvid,
        "stream_url": stream_url,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
