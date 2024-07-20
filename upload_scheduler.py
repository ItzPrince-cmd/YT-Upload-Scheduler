import os
import csv
import pickle
import datetime
import pytz
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Setup logging
logging.basicConfig(filename='upload_videos.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s:%(message)s')

# Scopes for YouTube Data API
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Base directory for video files
VIDEO_PATH = 'videos'
# Directory to save metadata CSV files
METADATA_PATH = 'metadata'
# File to keep track of uploaded videos
UPLOAD_LOG_FILE = 'upload_log.txt'

# Metadata for each channel
channels_metadata = {
    'channel1': {
        'title': 'Title for Channel 1',
        'description': 'Description for Channel 1',
        'tags': 'tag1,tag2,tag3'
    },
    'channel2': {
        'title': 'Title for Channel 2',
        'description': 'Description for Channel 2',
        'tags': 'tag4,tag5,tag6'
    },
    # Add metadata for more channels as needed
}

def generate_csv(channel_name, video_filenames, title, description, tags):
    csv_file = os.path.join(METADATA_PATH, f'{channel_name}.csv')
    os.makedirs(METADATA_PATH, exist_ok=True)
    
    existing_metadata = []
    if os.path.exists(csv_file):
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_metadata.append(row)

    # Atomic write
    temp_csv_file = f'{csv_file}.tmp'
    with open(temp_csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['filename', 'title', 'description', 'tags'])
        for row in existing_metadata:
            writer.writerow([row['filename'], row['title'], row['description'], row['tags']])
        for filename in video_filenames:
            if filename not in [row['filename'] for row in existing_metadata]:
                writer.writerow([filename, title, description, tags])
    os.replace(temp_csv_file, csv_file)

def list_video_filenames(channel_name):
    video_folder = os.path.join(VIDEO_PATH, channel_name)
    video_filenames = [filename for filename in os.listdir(video_folder) if os.path.isfile(os.path.join(video_folder, filename))]
    return video_filenames

def authenticate(channel_name):
    creds = None
    token_file = f'token_{channel_name}.pickle'
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logging.error(f"Failed to refresh credentials for {channel_name}: {e}")
                return None
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logging.error(f"Failed to authenticate for {channel_name}: {e}")
                return None
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    return build('youtube', 'v3', credentials=creds)

def read_metadata_from_csv(channel_name):
    metadata = []
    csv_file = os.path.join(METADATA_PATH, f'{channel_name}.csv')
    if os.path.exists(csv_file):
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                tags = row['tags'].split(',')
                metadata.append({
                    'filename': row['filename'],
                    'title': row['title'],
                    'description': row['description'],
                    'tags': tags
                })
    return metadata

def schedule_video_upload(youtube, video_path, title, description, tags, upload_time):
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '22'  # Adjust category ID if needed
        },
        'status': {
            'privacyStatus': 'private',
            'publishAt': upload_time.isoformat() + 'Z',  # Ensure proper formatting for time
            'selfDeclaredMadeForKids': False,
        },
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    response = None
    try:
        while response is None:
            status, response = request.next_chunk()
        logging.info(f'Uploaded: {title} scheduled for {upload_time}')
    except Exception as e:
        logging.error(f"Failed to upload {video_path}: {e}")
    return response

def get_upload_times(current_time, uploads_per_day):
    if uploads_per_day == 1:
        return [current_time.replace(hour=8, minute=0, second=0, microsecond=0)]
    else:
        return [
            current_time.replace(hour=8, minute=0, second=0, microsecond=0),
            current_time.replace(hour=12, minute=0, second=0, microsecond=0),
            current_time.replace(hour=15, minute=0, second=0, microsecond=0)
        ]

def load_uploaded_videos():
    if not os.path.exists(UPLOAD_LOG_FILE):
        return set()
    with open(UPLOAD_LOG_FILE, 'r') as file:
        uploaded_videos = set(line.strip() for line in file)
    return uploaded_videos

def save_uploaded_video(filename):
    with open(UPLOAD_LOG_FILE, 'a') as file:
        file.write(filename + '\n')

def main():
    uploaded_videos = load_uploaded_videos()

    # Part 1: Generate CSV files
    for channel_name, metadata in channels_metadata.items():
        video_filenames = list_video_filenames(channel_name)
        if not video_filenames:
            logging.info(f'No videos found for {channel_name}')
            continue
        title = metadata['title']
        description = metadata['description']
        tags = metadata['tags']
        generate_csv(channel_name, video_filenames, title, description, tags)
        logging.info(f'CSV file generated for {channel_name} with {len(video_filenames)} videos.')

    # Part 2: Schedule video uploads
    channels = [
        {'name': 'channel1', 'uploads_per_day': 3},
        {'name': 'channel2', 'uploads_per_day': 1},
        # Add more channels as needed with their respective upload counts
    ]

    for channel in channels:
        channel_name = channel['name']
        uploads_per_day = channel['uploads_per_day']
        metadata = read_metadata_from_csv(channel_name)
        youtube = authenticate(channel_name)
        if not youtube:
            logging.error(f"Skipping upload for {channel_name} due to authentication failure.")
            continue

        current_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))

        upload_times = get_upload_times(current_time, uploads_per_day)

        for i in range(uploads_per_day):
            if i >= len(metadata):
                logging.info(f'Not enough videos for {channel_name} to schedule {uploads_per_day} uploads.')
                break
            video = metadata[i]
            video_path = os.path.join(VIDEO_PATH, channel_name, video["filename"])
            title = video['title']
            description = video['description']
            tags = video['tags']

            if video["filename"] in uploaded_videos:
                logging.info(f'Skipping already uploaded video: {video["filename"]}')
                continue

            upload_time = upload_times[i]
            response = schedule_video_upload(youtube, video_path, title, description, tags, upload_time)
            
            if response:
                save_uploaded_video(video["filename"])

if __name__ == '__main__':
    main()
