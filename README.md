# 🎬 Video Streaming Website

A beautiful web-based video streaming server that allows you to access and stream your video collection from any device on your local network.

## ✨ Features

- 🎥 **Video Streaming** - Stream MP4, MKV, AVI, MOV, WMV, FLV, and WebM files
- 🌐 **Web-based Interface** - Access from any device with a web browser
- 📱 **Mobile-Friendly** - Responsive design works on phones and tablets
- 🎨 **Modern UI** - Beautiful gradient interface with animated backgrounds
- 🔍 **Search & Filter** - Search videos and filter by Movies/Series
- 📊 **Statistics** - View total files, video count, and storage usage
- 🎬 **Built-in Player** - Watch videos directly in the browser with controls
- 📋 **VLC Integration** - Copy streaming links to open in VLC Media Player
- 🔄 **Smart Streaming** - HTTP range support for seeking and partial loading
- 📁 **Organized Library** - Automatically categorizes Movies and Series

## 🚀 Quick Start

### Prerequisites

- Python 3.x installed on your system
- Video files organized in folders

### Installation

1. **Clone or download this project**

2. **Configure your video path:**
   - Edit the `.env` file and set `FILE_PATH` to your video directory:
   ```
   FILE_PATH=C:\Users\YourName\Videos
   ```

### Running the Server

**Option 1: Use the batch file (Windows)**
```cmd
start_server.bat
```

**Option 2: Run directly with Python**
```cmd
python server.py
```

### Accessing the Website

- **Local machine:** http://localhost:8001 or http://127.0.0.1:8001
- **Other devices:** Use the IP address shown in the server output (e.g., http://192.168.1.100:8001)

### Stopping the Server

- Press `Ctrl+C` in the terminal where the server is running

## 📁 Organizing Your Videos

For best results, organize your videos like this:

```
Videos/
├── Movies/
│   ├── Movie1.mp4
│   ├── Movie2.mkv
│   └── Movie3.avi
└── Series/
    ├── Series Name 1/
    │   ├── S01E01.mp4
    │   └── S01E02.mp4
    └── Series Name 2/
        ├── Episode 1.mkv
        └── Episode 2.mkv
```

The server will automatically:
- Categorize files in `Movies/` folder as movies
- Group files in `Series/` subfolders by series name
- Display appropriate filters and metadata

## 🎮 How to Use

1. **Browse Videos** - Scroll through your video library
2. **Search** - Use the search bar to find specific videos
3. **Filter** - Click filter buttons (All/Videos/Movies/Series)
4. **Watch** - Click a video card to play it in the browser
5. **VLC Link** - Click "📋 Copy VLC Link" to open in VLC Media Player
6. **Refresh** - Click the refresh button to reload the file list

## 🔧 How It Works

1. **Server Setup:** Python script starts a web server on port 8001
2. **Network Access:** Server binds to all network interfaces for remote access
3. **File Discovery:** Automatically scans configured directory for videos
4. **JSON API:** Provides `/files.json` endpoint with video metadata
5. **Web Interface:** Beautiful HTML/CSS/JS interface for browsing and playback
6. **Range Support:** Implements HTTP range requests for video seeking

## 🔒 Security Notes

- ⚠️ **Local Network Only:** Videos accessible only from devices on same network
- 🔐 **No Authentication:** Anyone on your network can access the videos
- 🚫 **Read-Only:** No upload or modification capabilities
- 📁 **Configured Directory:** Only serves files from the configured `FILE_PATH`

## 🐛 Troubleshooting

### Server Won't Start

- **Port in use:** Check if port 8001 is already in use
  ```cmd
  netstat -ano | findstr :8001
  ```
- **Kill process:** If needed, kill the process using the port
- **Change port:** Edit `server.py` and modify the `port` variable

### Can't Access from Other Devices

- Ensure both devices are on the same Wi-Fi network
- Check firewall settings (allow Python through Windows Firewall)
- Verify the IP address shown in server output
- Try temporarily disabling firewall to test

### Videos Not Playing

- Ensure videos are in the configured `FILE_PATH` directory
- Check video file format is supported (MP4 works best)
- Try opening the VLC link in VLC Media Player
- Check browser console for errors (F12)

### Files Not Showing

- Verify `FILE_PATH` in `.env` file is correct
- Ensure directory exists and Python has read permissions
- Check server console for error messages
- Try the refresh button

## 🎨 Customization

### Change Port

Edit `server.py` and change the port variable:
```python
port = 8080  # Change from 8001 to your preferred port
```

### Change Video Path

Edit `.env` file:
```
FILE_PATH=D:\MyVideos
```

### Customize Interface

Edit `index.html` to modify:
- Colors and gradients
- Layout and grid
- Features and functionality

## 🛠️ Technical Details

- **Backend:** Python 3 with `http.server`, `socketserver`, and `python-dotenv`
- **Frontend:** Vanilla HTML5, CSS3, and JavaScript
- **Video Streaming:** HTTP range requests for progressive streaming
- **API:** RESTful JSON endpoint for file listing
- **CORS:** Enabled for cross-origin requests
- **Responsive:** Mobile-first design with CSS Grid and Flexbox
- **Port:** 8001 (configurable)

## 📦 Project Structure

```
streaming_website/
├── server.py           # Python server with streaming support
├── index.html          # Web interface
├── .env               # Configuration (video path)
├── .env.example       # Template configuration file
├── start_server.bat   # Windows batch file to start server
├── README.md          # This file
└── __pycache__/       # Python cache (auto-generated)
```

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Credits

Made with ❤️ for personal video streaming
