import os
import re
import datetime
import xml.etree.ElementTree as ET

# Configuration
BASE_URL = "https://amletdotco.github.io/fotf-ainran/audio"
ARTWORK_URL = "https://amletdotco.github.io/fotf-ainran/images/podcast_artwork.png"
OUTPUT_FILE = "podcast_feed.xml"
PODCAST_TITLE = "The Chronicles of Narnia (Radio Theatre)"
PODCAST_DESCRIPTION = "Focus on the Family's The Chronicles of Narnia Radio Theatre"
PODCAST_LANGUAGE = "en-us"
PODCAST_LINK = "https://amletdotco.github.io/fotf-ainran/"

NARNIA_ORDER = [
    "The Magicians Nephew",
    "The Lion the Witch and the Wardrobe",
    "The Horse and His Boy",
    "Prince Caspian",
    "The Voyage of the Dawn Treader",
    "The Silver Chair",
    "The Last Battle",
]


def normalize_string(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def prettify_name(file_name):
    # Remove extension
    name = os.path.splitext(file_name)[0]
    # Remove leading numeric prefix and underscore
    name = re.sub(r"^\d+_", "", name)
    name = name.replace("_", " ").strip()
    return name, None  # No longer extracting part info for sorting purposes


def get_book_order(file_name):
    file_normalized = normalize_string(file_name)
    for index, book in enumerate(NARNIA_ORDER):
        book_normalized = normalize_string(book)
        if book_normalized in file_normalized:
            return index
    return float("inf")


def get_numeric_prefix(file_name):
    match = re.match(r"^(\d+)", file_name)
    if match:
        return int(match.group(1))
    return 999999999


def generate_rss(audio_folder):
    rss = ET.Element(
        "rss",
        version="2.0",
        attrib={"xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"},
    )
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = PODCAST_TITLE
    ET.SubElement(channel, "link").text = PODCAST_LINK
    ET.SubElement(channel, "description").text = PODCAST_DESCRIPTION
    ET.SubElement(channel, "language").text = PODCAST_LANGUAGE
    ET.SubElement(channel, "itunes:image", href=ARTWORK_URL)

    audio_files = [
        file_name
        for file_name in os.listdir(audio_folder)
        if file_name.endswith(".mp3")
    ]
    # Sort by book order then by numeric prefix
    audio_files.sort(key=lambda f: (get_book_order(f), get_numeric_prefix(f)))

    total = len(audio_files)
    base_date = datetime.datetime.now()

    # Assign dates so the first item in the sorted list is the oldest.
    # If you actually prefer the first item to be oldest, we can keep the order:
    # index 0 is oldest -> idx = 0 -> no offset or negative offset needed.
    for idx, file_name in enumerate(audio_files):
        file_path = os.path.join(audio_folder, file_name)
        file_url = f"{BASE_URL}/{file_name}"
        file_size = os.path.getsize(file_path)

        title, _ = prettify_name(file_name)
        description = f"Description for {title}"

        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "description").text = description
        ET.SubElement(
            item,
            "enclosure",
            {"url": file_url, "length": str(file_size), "type": "audio/mpeg"},
        )

        # Assign a date in ascending order (first file is oldest)
        pub_date = (base_date - datetime.timedelta(days=(total - idx - 1))).strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )
        ET.SubElement(item, "pubDate").text = pub_date

    tree = ET.ElementTree(rss)
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print(f"RSS feed generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    audio_folder = "audio"
    if not os.path.exists(audio_folder):
        print(f"Error: Folder '{audio_folder}' does not exist.")
    else:
        generate_rss(audio_folder)
