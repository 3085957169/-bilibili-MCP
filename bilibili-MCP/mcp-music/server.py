import os
import subprocess
import sys
import httpx
from mcp.server import FastMCP

BASE_URL = os.environ.get("MUSIC_BASE_URL", "http://47.108.64.39:50282")
API_TIMEOUT = 60.0

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
async def list_songs() -> list[dict]:
    """List all downloaded/converted audio files available in the music library."""
    async with await _client() as client:
        r = await client.get(f"{BASE_URL}/api/songs")
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def download_song(bvid: str, title: str) -> dict:
    """Download a Bilibili video and convert it to audio. Requires the video bvid (e.g. BV1xx411c7mD) and a title.

    Use search_videos first to find the bvid and title of the video you want.
    """
    async with await _client() as client:
        r = await client.post(
            f"{BASE_URL}/api/download",
            json={"bvid": bvid, "title": title},
        )
        r.raise_for_status()
        return r.json()


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


if __name__ == "__main__":
    mcp.run(transport="stdio")
