"""从库街区 Wiki 下载角色头像和编队立绘。"""
import logging
import re
from pathlib import Path

import requests
from PySide6.QtCore import QThread, Signal

from core.config import get_resource_path

logger = logging.getLogger(__name__)

_PAGE_URL = "https://api.kurobbs.com/wiki/core/catalogue/item/getPage"
_DETAIL_URL = "https://api.kurobbs.com/wiki/core/catalogue/item/getEntryDetail"
_AVATAR_CATALOGUE = "1363"
_CHARACTER_CATALOGUE = "1105"
_INVALID_FILENAME = re.compile(r'[<>:"/\\|?*]')
_ACTIVE_SYNCS = []


def _headers():
    return {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Origin": "https://wiki.kurobbs.com",
        "Referer": "https://wiki.kurobbs.com/",
        "User-Agent": "Mozilla/5.0",
        "wiki_type": "9",
    }


def _image_headers():
    return {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://wiki.kurobbs.com/",
    }


def safe_character_name(name):
    """把角色名整理成 Windows 文件名。"""
    cleaned = _INVALID_FILENAME.sub("", (name or "").strip())
    return cleaned.rstrip(". ")


def asset_exists(directory, name):
    for suffix in (".png", ".webp", ".jpg", ".jpeg"):
        if (directory / f"{name}{suffix}").exists():
            return True
    return False


def _post_json(url, data):
    response = requests.post(url, headers=_headers(), data=data, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != 200:
        raise RuntimeError(payload.get("msg") or "Wiki 接口返回失败")
    return payload


def iter_catalogue(catalogue_id):
    """翻页读取图鉴条目。"""
    page = 1
    while True:
        payload = _post_json(_PAGE_URL, {
            "catalogueId": catalogue_id,
            "page": page,
            "pageSize": 200,
        })
        results = (payload.get("data") or {}).get("results") or {}
        records = results.get("records") or []
        for record in records:
            yield record
        total_pages = int(results.get("pages") or 1)
        if page >= total_pages:
            break
        page += 1


def entry_id_of(record):
    content = record.get("content") or {}
    link = (content.get("linkConfig") or {}).get("entryId")
    return str(link or record.get("entryId") or "")


def portrait_url_from_detail(payload):
    """角色详情里的编队立绘，用作窗口左下角的全身图。"""
    content = (payload.get("data") or {}).get("content") or {}
    for module in content.get("modules") or []:
        for component in module.get("components") or []:
            for figure in (component.get("role") or {}).get("figures") or []:
                if figure.get("name") == "编队立绘" and figure.get("url"):
                    return figure["url"]
    return ""


def _download(url, destination):
    response = requests.get(url, headers=_image_headers(), timeout=60)
    response.raise_for_status()
    if not response.content:
        raise RuntimeError("图片内容为空")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(response.content)


def sync_character_assets(progress=None):
    """下载缺失的头像和立绘。已有同名文件保持不变。"""
    def report(message):
        logger.info("%s", message)
        if progress:
            progress(message)

    profile_dir = get_resource_path("resources/profile")
    character_dir = get_resource_path("resources/characters")
    profile_dir.mkdir(parents=True, exist_ok=True)
    character_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "avatars": 0,
        "portraits": 0,
        "skipped": 0,
        "failed": 0,
    }

    report("正在获取头像列表...")
    avatars = list(iter_catalogue(_AVATAR_CATALOGUE))
    for index, record in enumerate(avatars, start=1):
        name = safe_character_name(record.get("name"))
        url = (record.get("content") or {}).get("contentUrl") or ""
        report(f"头像 {index}/{len(avatars)} {name}")
        if not name or not url:
            summary["failed"] += 1
            continue
        if asset_exists(profile_dir, name):
            summary["skipped"] += 1
            continue
        try:
            _download(url, profile_dir / f"{name}.png")
            summary["avatars"] += 1
        except Exception as exc:
            summary["failed"] += 1
            logger.warning("下载头像失败 %s: %s", name, exc)

    report("正在获取角色列表...")
    characters = list(iter_catalogue(_CHARACTER_CATALOGUE))
    for index, record in enumerate(characters, start=1):
        name = safe_character_name(record.get("name"))
        report(f"立绘 {index}/{len(characters)} {name}")
        if not name:
            summary["failed"] += 1
            continue
        if asset_exists(character_dir, name):
            summary["skipped"] += 1
            continue
        entry_id = entry_id_of(record)
        if not entry_id:
            summary["failed"] += 1
            continue
        try:
            detail = _post_json(_DETAIL_URL, {"id": entry_id})
            url = portrait_url_from_detail(detail)
            if not url:
                summary["failed"] += 1
                logger.warning("未找到编队立绘: %s", name)
                continue
            _download(url, character_dir / f"{name}.png")
            summary["portraits"] += 1
        except Exception as exc:
            summary["failed"] += 1
            logger.warning("下载立绘失败 %s: %s", name, exc)

    report(
        f"完成：新头像 {summary['avatars']}，新立绘 {summary['portraits']}，"
        f"已存在跳过 {summary['skipped']}，失败 {summary['failed']}"
    )
    return summary


class CharacterAssetSync(QThread):
    """后台同步角色头像和立绘。"""
    progress = Signal(str)
    finished_ok = Signal(dict)
    failed = Signal(str)

    def run(self):
        try:
            summary = sync_character_assets(self.progress.emit)
            self.finished_ok.emit(summary)
        except Exception as exc:
            logger.error("同步角色形象失败: %s", exc)
            self.failed.emit(str(exc))


def start_character_asset_sync(on_progress, on_success, on_error):
    """启动同步并持有线程，避免窗口关闭后线程被销毁。"""
    thread = CharacterAssetSync()
    _ACTIVE_SYNCS.append(thread)

    def _drop():
        if thread in _ACTIVE_SYNCS:
            _ACTIVE_SYNCS.remove(thread)

    thread.progress.connect(on_progress)
    thread.finished_ok.connect(on_success)
    thread.failed.connect(on_error)
    thread.finished.connect(_drop)
    thread.finished.connect(thread.deleteLater)
    thread.start()
    return thread
