# Automated YouTube Video Uploader

This script is designed to automate the process of uploading videos to YouTube using the YouTube Data API. It automates the process of uploading videos to multiple YouTube channels. It includes functionalities for generating metadata, scheduling video uploads, and logging uploaded videos.

## Table of Contents

- [Folder Structure](#folder-structure)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Configuration](#configuration)
- [Running the Script](#running-the-script)
- [Automating with Cron](#automating-with-cron)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)

## Folder Structure

The project directory should be organized as follows:

```
/path/to/your/project
├── venv/
├── videos/
│   ├── channel1/
│   │   ├── video1.mp4
│   │   ├── video2.mp4
│   │   └── ...
│   ├── channel2/
│   │   ├── video1.mp4
│   │   └── ...
│   └── ... (more channels if needed)
├── metadata/
│   ├── channel1.csv
│   ├── channel2.csv
│   └── ... (more CSV files for other channels)
├── client_secret.json
├── upload_log.txt
├── upload_videos.py
└── cron_log.txt
```

### Explanation

- **`venv/`**: Virtual environment directory containing installed Python packages.
- **`videos/`**: Directory for storing video files. Each channel has its own subdirectory.
- **`metadata/`**: Directory for storing metadata CSV files generated by the script.
- **`client_secret.json`**: OAuth 2.0 client secrets file from Google Cloud for API authentication.
- **`upload_log.txt`**: Log file for tracking uploaded videos.
- **`upload_videos.py`**: Main Python script for uploading videos.
- **`cron_log.txt`**: Log file for cron job output.

## Prerequisites

- Python 3.8 or higher
- Pip
- Google Cloud project with YouTube Data API enabled
- OAuth 2.0 client credentials (`client_secret.json`)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/automated-youtube-uploader.git
cd automated-youtube-uploader
```

### 2. Create Project Directory Structure

```bash
mkdir -p videos metadata
mkdir -p videos/channel1 videos/channel2
```

### 3. Set Up a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Required Python Libraries

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 5. Add OAuth 2.0 Client Credentials

Download `client_secret.json` from your Google Cloud project and place it in the project directory.

## Configuration

### Metadata Configuration

Define metadata for each channel in the `upload_videos.py` script:

```python
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
```

### Channel Upload Configuration

Define the number of uploads per day for each channel in the `main` function:

```python
channels = [
    {'name': 'channel1', 'uploads_per_day': 3},
    {'name': 'channel2', 'uploads_per_day': 1},
    # Add more channels as needed with their respective upload counts
]
```

## Running the Script

### 1. Activate the Virtual Environment

```bash
source /path/to/your/project/venv/bin/activate
```

### 2. Run the Script Manually

```bash
python upload_videos.py
```

### 3. Check the Output

Ensure CSV files are generated and videos are scheduled for upload. Uploaded videos are logged in `upload_log.txt`.

## Automating with Cron

### 1. Open Crontab for Editing

```bash
crontab -e
```

### 2. Add the Cron Job Entry

```bash
0 2 * * * source /path/to/your/project/venv/bin/activate && /path/to/your/project/venv/bin/python /path/to/your/project/upload_videos.py >> /path/to/your/project/cron_log.txt 2>&1
```

This sets the script to run daily at 2 AM.

### 3. Verify Cron Job

```bash
crontab -l
```

### 4. Monitor Cron Job Execution

```bash
cat /path/to/your/project/cron_log.txt
```

## Logging

- **`upload_log.txt`**: Contains a record of uploaded video filenames to prevent re-uploads.
- **`cron_log.txt`**: Contains the output of the cron job for monitoring and debugging.

## Troubleshooting

- Ensure `client_secret.json` is correctly placed in the project directory.
- Verify internet connectivity for API authentication and video uploads.
- Check `cron_log.txt` for any errors or issues with the cron job execution.
- Ensure the virtual environment is activated before running the script manually.

## Contributing

Feel free to submit issues, fork the repository, and send pull requests. Contributions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
