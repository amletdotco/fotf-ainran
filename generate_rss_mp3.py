import os
import re
import datetime
import xml.etree.ElementTree as ET

# Configuration
BASE_URL = "https://amletdotco.github.io/fotf-ainran/audio"  # Base URL for audio files
ARTWORK_URL = "https://amletdotco.github.io/fotf-ainran/images/podcast_artwork.png"  # URL for podcast artwork
OUTPUT_FILE = "podcast_feed.xml"  # Output RSS file
PODCAST_TITLE = "The Chronicles of Narnia (Radio Theatre)"
PODCAST_DESCRIPTION = "Focus on the Family's The Chronicles of Narnia Radio Theatre"
PODCAST_LANGUAGE = "en-us"
PODCAST_LINK = "https://amletdotco.github.io/fotf-ainran/"  # Podcast homepage

# Narnia books in chronological order
NARNIA_ORDER = [
    "The Magician's Nephew",
    "The Lion, the Witch and the Wardrobe",
    "The Horse and His Boy",
    "Prince Caspian",
    "The Voyage of the Dawn Treader",
    "The Silver Chair",
    "The Last Battle",
]


# Helper function to prettify episode names
def prettify_name(file_name):
    name = os.path.splitext(file_name)[0]
    name = re.sub(r"^\d+_", "", name)  # Remove leading numbers
    name = name.replace("_", " ").strip()  # Replace underscores with spaces
    part_match = re.search(r"(Part \d+ of \d+)", name, flags=re.IGNORECASE)
    if part_match:
        part_info = part_match.group(1)
        name = re.sub(r"\s*\(Part \d+ of \d+\)", "", name)  # Remove duplicate part info
        name += f" ({part_info})"  # Append prettified part info
    return name


# Extract book name from the file name and find its order
def get_book_order(file_name):
    for index, book in enumerate(NARNIA_ORDER):
        if book.lower() in file_name.lower():
            return index
    return float("inf")  # Default to end of list if not found


# Generate the RSS feed
def generate_rss(audio_folder):
    # Create root RSS element
    rss = ET.Element(
        "rss",
        version="2.0",
        attrib={"xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"},
    )
    channel = ET.SubElement(rss, "channel")

    # Add podcast metadata
    ET.SubElement(channel, "title").text = PODCAST_TITLE
    ET.SubElement(channel, "link").text = PODCAST_LINK
    ET.SubElement(channel, "description").text = PODCAST_DESCRIPTION
    ET.SubElement(channel, "language").text = PODCAST_LANGUAGE
    ET.SubElement(channel, "itunes:image", href=ARTWORK_URL)  # Add podcast artwork

    # Get all audio files and sort by book order
    audio_files = [
        file_name
        for file_name in os.listdir(audio_folder)
        if file_name.endswith(".mp3")
    ]
    audio_files.sort(key=lambda f: (get_book_order(f), prettify_name(f)))

    # Generate publish dates in ascending order
    base_date = datetime.datetime.now() - datetime.timedelta(days=len(audio_files))
    for idx, file_name in enumerate(audio_files):
        file_path = os.path.join(audio_folder, file_name)
        file_url = f"{BASE_URL}/{file_name}"
        file_size = os.path.getsize(file_path)

        # Create an <item> element for each episode
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = prettify_name(file_name)
        ET.SubElement(item, "description").text = (
            f"Description for {prettify_name(file_name)}"
        )
        ET.SubElement(
            item,
            "enclosure",
            {"url": file_url, "length": str(file_size), "type": "audio/mpeg"},
        )
        pub_date = (base_date + datetime.timedelta(days=idx)).strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )
        ET.SubElement(item, "pubDate").text = pub_date

    # Write the RSS feed to the output file
    tree = ET.ElementTree(rss)
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print(f"RSS feed generated: {OUTPUT_FILE}")


# Main script
if __name__ == "__main__":
    audio_folder = "audio"  # Path to your audio folder
    if not os.path.exists(audio_folder):
        print(f"Error: Folder '{audio_folder}' does not exist.")
    else:
        generate_rss(audio_folder)
