import gzip
import json
import os
import shutil
import sys
import zipfile

from kotatsu import *

# импорт protobuf-сгенерированных файлов
import neko_pb2 as neko


def neko_to_kotatsu(input_path: str, output_path: str):
    try:
        print(f"[I] Loading file: {input_path}")
        with gzip.GzipFile(input_path, 'rb') as f:
            neko_read = f.read()
    except gzip.BadGzipFile:
        print(f"[E] Bad file: {input_path}")
        return

    # Заменяем prost.decode на protobuf
    backup = neko.Backup()
    backup.ParseFromString(neko_read)

    result_categories = []
    result_favourites = []
    result_history = []
    result_bookmarks = []

    manga_counter = 0

    for i, category in enumerate(backup.backupCategories):
        result_categories.append(KotatsuCategoryBackup(
            category_id=i + 1,
            created_at=0,
            sort_key=category.order,
            title=category.name,
            order=None,
            track=None,
            show_in_lib=None,
            deleted_at=0
        ))

    for manga in backup.backupManga:
        manga_counter += 1
        manga_url = manga.url.replace("/manga/", "")
        kotatsu_manga = KotatsuMangaBackup(
            id=get_kotatsu_id("MANGADEX", manga_url),
            title=manga.title,
            alt_title=None,
            url=manga_url,
            public_url=f"https://mangadex.org/title/{manga_url}",
            rating=-1.0,
            nsfw=False,
            cover_url=f"{manga.thumbnailUrl}",
            large_cover_url=manga.thumbnailUrl,
            author=manga.author,
            state={
                1: "ONGOING",
                2: "FINISHED",
                4: "FINISHED",
                5: "ABANDONED",
                6: "PAUSED",
            }.get(manga.status, ""),
            source="MANGADEX",
            tags=[],
        )

        if manga.categories:
            for category_id in manga.categories:
                result_favourites.append(KotatsuFavouriteBackup(
                    manga_id=kotatsu_manga.id,
                    category_id=category_id + 1,
                    sort_key=0,
                    created_at=0,
                    deleted_at=0,
                    manga=kotatsu_manga,
                ))

        latest_chapter = max(
            (checking for checking in manga.chapters if checking.read),
            default=None,
            key=lambda checking: checking.chapterNumber,
        )

        bookmarks = [
            KotatsuBookmarkEntry(
                manga_id=kotatsu_manga.id,
                page_id=0,
                chapter_id=get_kotatsu_id("MANGADEX", checking.url.replace("/chapter/", "")),
                page=checking.lastPageRead,
                scroll=0,
                image_url=kotatsu_manga.cover_url,
                created_at=0,
                percent=(checking.lastPageRead / (
                        checking.lastPageRead + checking.pagesLeft))
                if checking.lastPageRead + checking.pagesLeft > 0 else 0.0,
            )
            for checking in manga.chapters if checking.bookmark
        ]

        if bookmarks:
            result_bookmarks.append(KotatsuBookmarkBackup(
                manga=kotatsu_manga,
                tags=[],
                bookmarks=bookmarks,
            ))

        newest_cached_chapter = max(manga.chapters, key=lambda a: a.chapterNumber, default=None)

        last_read = max((entry.lastRead for entry in manga.history), default=manga.lastUpdate)

        kotatsu_history = KotatsuHistoryBackup(
            manga_id=kotatsu_manga.id,
            created_at=manga.dateAdded,
            updated_at=last_read,
            chapter_id=(latest_chapter and get_kotatsu_id("MANGADEX",
                                                          latest_chapter.url.replace("/chapter/", ""))) or 0,
            page=(latest_chapter and latest_chapter.lastPageRead) or 0,
            scroll=0.0,
            percent=(
                    (latest_chapter and newest_cached_chapter and (
                            (getattr(latest_chapter, 'chapterNumber',
                                     0) - 1.0) / newest_cached_chapter.chapterNumber) if getattr(
                        newest_cached_chapter, 'chapterNumber', 1) > 0 else 0) or 0.0
            ),
            manga=kotatsu_manga,
        )

        result_history.append(kotatsu_history)

    tmp = "_tmp"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    os.mkdir(tmp)
    filenames = []
    for name, entry in [
        ("history", [entry.to_dict() for entry in result_history]),
        ("categories", [entry.to_dict() for entry in result_categories]),
        ("favourites", [entry.to_dict() for entry in result_favourites]),
        ("bookmarks", [entry.to_dict() for entry in result_bookmarks]),
    ]:
        if entry:
            with open(f"{tmp}/{name}", 'w') as f:
                j = json.dumps(entry)
                f.write(j)
                filenames.append([f"{tmp}/{name}", name])

    print(f"[I] Loaded mangas: {manga_counter}")

    with zipfile.ZipFile(f"kotasu_{output_path}.bk.zip", mode="w") as archive:
        for filename, name in filenames:
            archive.write(filename, name)
            print(f"[I] {filename} - added")
    shutil.rmtree(tmp)

    print(f"Conversion completed successfully\nCheck it in: 'kotasu_{output_path}.bk.zip'")


def main():
    args = sys.argv

    if "-h" in args or "--help" in args:
        print(f"Usage: {args[0]} FILE [output_dir]"
              f"\n  FILE - Neko gzipped backup"
              f"\n  [output_dir] - [OPTIONAL] dir where safe files (Default - name of FILE)")
        return

    if len(args) < 2:
        print(f"Usage: {args[0]} FILE [output dir]\n  {args[0]} -h for help.")
        return

    input_path = args[1]
    output_path = args[2] if len(args) > 2 else os.path.basename(".".join(input_path.split(".")[:-1]))

    if os.path.exists(f"kotasu_{output_path}.bk.zip"):
        overwrite = input(f"[I] File with name 'kotasu_{output_path}.bk.zip' already exists\nOverwrite? Y(es)/N(o): ").strip().lower()
        if overwrite not in {"y", "yes"}:
            print("Conversion cancelled")
            return
        os.remove(f"kotasu_{output_path}.bk.zip")

    neko_to_kotatsu(input_path, output_path)
    input("\nPress enter to exit...")


if __name__ == "__main__":
    main()
