# kotatsu.py

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class KotatsuMangaBackup:
    id: int
    title: str
    alt_title: Optional[str]
    url: str
    public_url: str
    rating: float
    nsfw: bool
    cover_url: str
    large_cover_url: Optional[str]
    state: str
    author: str
    source: str
    tags: List[str]  # changed from array to list

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'alt_title': self.alt_title,
            'url': self.url,
            'public_url': self.public_url,
            'rating': self.rating,
            'nsfw': self.nsfw,
            'cover_url': self.cover_url,
            'large_cover_url': self.large_cover_url,
            'state': self.state,
            'author': self.author,
            'source': self.source,
            'tags': self.tags,
        }


@dataclass
class KotatsuHistoryBackup:
    manga_id: int
    created_at: int
    updated_at: int
    chapter_id: int
    page: int
    scroll: float
    percent: float
    manga: KotatsuMangaBackup

    def to_dict(self):
        return {
            'manga_id': self.manga_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'chapter_id': self.chapter_id,
            'page': self.page,
            'scroll': self.scroll,
            'percent': self.percent,
            'manga': self.manga.to_dict(),
        }


@dataclass
class KotatsuCategoryBackup:
    category_id: int
    created_at: int
    sort_key: int
    title: str
    order: Optional[str]
    track: Optional[bool]
    show_in_lib: Optional[bool]
    deleted_at: int

    def to_dict(self):
        return {
            'category_id': self.category_id,
            'created_at': self.created_at,
            'sort_key': self.sort_key,
            'title': self.title,
            'order': self.order,
            'track': self.track,
            'show_in_lib': self.show_in_lib,
            'deleted_at': self.deleted_at,
        }


@dataclass
class KotatsuFavouriteBackup:
    manga_id: int
    category_id: int
    sort_key: int
    created_at: int
    deleted_at: int
    manga: KotatsuMangaBackup

    def to_dict(self):
        return {
            'manga_id': self.manga_id,
            'category_id': self.category_id,
            'sort_key': self.sort_key,
            'created_at': self.created_at,
            'deleted_at': self.deleted_at,
            'manga': self.manga.to_dict(),
        }


@dataclass
class KotatsuBookmarkEntry:
    manga_id: int
    page_id: int
    chapter_id: int
    page: int
    scroll: int
    image_url: str
    created_at: int
    percent: float

    def to_dict(self):
        return {
            'manga_id': self.manga_id,
            'page_id': self.page_id,
            'chapter_id': self.chapter_id,
            'page': self.page,
            'scroll': self.scroll,
            'image_url': self.image_url,
            'created_at': self.created_at,
            'percent': self.percent,
        }


@dataclass
class KotatsuBookmarkBackup:
    manga: KotatsuMangaBackup
    tags: List[str]
    bookmarks: List[KotatsuBookmarkEntry]

    def to_dict(self):
        return {
            'manga': self.manga.to_dict(),
            'tags': self.tags,
            'bookmarks': [bookmark.to_dict() for bookmark in self.bookmarks],
        }


def get_kotatsu_id(source_name: str, url: str) -> int:
    id = 1125899906842597
    for c in source_name:
        id = (31 * id + ord(c)) & ((1 << 63) - 1)
    for c in url:
        id = (31 * id + ord(c)) & ((1 << 63) - 1)
    return id
