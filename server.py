#!/usr/bin/env python3
"""
Simple HTTP Server for Remote File Access
Serves files from the current directory over the network.
Access from any device on the same network using the server's IP address.
"""

import http.server
import socketserver
import socket
import sys
import os
import json
from urllib.parse import unquote
from dotenv import load_dotenv
load_dotenv()
FILE_PATH = os.getenv('FILE_PATH')
if not FILE_PATH:
    print("Warning: FILE_PATH not set in .env. Defaulting to current directory.")
    FILE_PATH = os.getcwd()

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        """Translate URL path to filesystem path relative to FILE_PATH"""
        # Get the path from the parent class (this handles URL decoding)
        path = super().translate_path(path)
        
        # If it's trying to access index.html or root, allow it from current directory
        if path.endswith('index.html') or os.path.basename(path) == os.path.basename(os.getcwd()):
            return path
        
        # For video files, redirect to FILE_PATH
        rel_path = os.path.relpath(path, os.getcwd())
        if rel_path.startswith('..'):
            # Path is outside current directory, just return it
            return path
        
        # Construct path relative to FILE_PATH for video files
        new_path = os.path.join(os.path.abspath(FILE_PATH), rel_path)
        if os.path.exists(new_path):
            return new_path
        
        # Fall back to original path
        return path
    
    def end_headers(self):
        # Add CORS headers to allow cross-origin requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With')
        super().end_headers()

    def do_GET(self):
        print(f"Received request for: {self.path}")  # Debug log
        if self.path == '/files.json':
            print("Handling files.json request")  # Debug log
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Get list of files in current directory and subdirectories
            movies = []
            series_dict = {}
            base_path = os.path.abspath(FILE_PATH)
            print(f"Listing files from directory: {base_path}")  # Debug log
            try:
                for root, dirs, filenames in os.walk(base_path):
                    for filename in filenames:
                        # Skip hidden files, system files, and non-video files
                        if filename.startswith('.') or filename.lower() in ['desktop.ini', 'thumbs.db']:
                            continue
                        if filename.lower().endswith(('.pfl', '.zip', '.rar', '.7z', '.tar', '.gz')):
                            continue
                        
                        file_path = os.path.join(root, filename)
                        try:
                            file_size = os.path.getsize(file_path)
                            # Determine file type based on extension
                            if filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v')):
                                file_type = 'video'
                            elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                                file_type = 'image'
                            elif filename.lower().endswith(('.mp3', '.wav', '.flac', '.aac', '.ogg')):
                                file_type = 'audio'
                            elif filename.lower().endswith(('.txt', '.md', '.py', '.html', '.css', '.js')):
                                file_type = 'text'
                            else:
                                file_type = 'unknown'

                            # Show only the file name (not the path) for display
                            display_name = filename
                            rel_path = os.path.relpath(file_path, base_path)
                            
                            # Quick validation - only check if it's a file, skip expensive access checks
                            if not os.path.isfile(file_path):
                                continue
                            rel_path = os.path.relpath(file_path, base_path)
                            top_folder = rel_path.split(os.sep)[0].lower() if os.sep in rel_path else ''
                            entry = {
                                'name': display_name,
                                'path': rel_path,
                                'size': file_size,
                                'type': file_type,
                                'modified': os.path.getmtime(file_path)
                            }
                            if top_folder == 'movies':
                                movies.append(entry)
                                print(f"Added movie: {display_name}")
                            elif top_folder == 'series':
                                # For series, group by the next folder (series name)
                                rel_parts = rel_path.split(os.sep)
                                if len(rel_parts) > 1:
                                    series_name = rel_parts[1]
                                    if series_name not in series_dict:
                                        series_dict[series_name] = []
                                    series_dict[series_name].append(entry)
                                    print(f"Added to series '{series_name}': {display_name}")
                                else:
                                    # If file is directly under 'series', treat as a single-episode series
                                    series_name = display_name
                                    if series_name not in series_dict:
                                        series_dict[series_name] = []
                                    series_dict[series_name].append(entry)
                                    print(f"Added single-episode series: {display_name}")
                            else:
                                movies.append(entry)  # Default to movies if not in a folder
                                print(f"Added (default movie): {display_name}")
                        except (OSError, IOError) as e:
                            print(f"Error accessing file {file_path}: {e}")
                            continue
            except Exception as e:
                print(f"Error listing files: {e}")
                import traceback
                traceback.print_exc()

            # Convert series_dict to a list of objects: {name, files}
            series = [{'name': name, 'files': files} for name, files in series_dict.items()]
            print(f"Returning {len(movies)} movies and {len(series)} series")  # Debug log
            self.wfile.write(json.dumps({'movies': movies, 'series': series}).encode())
            return

        # Handle video files with HTTP Range support for streaming
        if self.path.endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm')):
            # Properly decode URL and handle file paths
            from urllib.parse import unquote
            decoded_path = unquote(self.path)
            rel_path = decoded_path.lstrip('/')
            # Ensure proper path separators for the OS
            rel_path = rel_path.replace('/', os.sep)
            file_path = os.path.join(os.path.abspath(FILE_PATH), rel_path)
            
            print(f"Requested file path: {decoded_path}")
            print(f"Relative path: {rel_path}")
            print(f"Looking for file at: {file_path}")
            
            if os.path.exists(file_path):
                extension = self.path.split('.')[-1].lower()
                mime_types = {
                    'mp4': 'video/mp4',
                    'mkv': 'video/x-matroska',
                    'avi': 'video/x-msvideo',
                    'mov': 'video/quicktime',
                    'wmv': 'video/x-ms-wmv',
                    'flv': 'video/x-flv',
                    'webm': 'video/webm'
                }
                mime_type = mime_types.get(extension, 'video/mp4')

                file_size = os.path.getsize(file_path)
                range_header = self.headers.get('Range', None)
                if range_header:
                    # Parse Range header
                    bytes_range = range_header.replace('bytes=', '').split('-')
                    try:
                        start = int(bytes_range[0]) if bytes_range[0] else 0
                        end = int(bytes_range[1]) if len(bytes_range) > 1 and bytes_range[1] else file_size - 1
                    except ValueError:
                        start = 0
                        end = file_size - 1
                    if end >= file_size:
                        end = file_size - 1
                    chunk_size = end - start + 1
                    self.send_response(206)
                    self.send_header('Content-type', mime_type)
                    self.send_header('Accept-Ranges', 'bytes')
                    self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
                    self.send_header('Content-Length', str(chunk_size))
                    self.send_header('Cache-Control', 'no-cache')
                    # Do NOT set Content-Disposition for streaming
                    self.end_headers()
                    try:
                        with open(file_path, 'rb') as f:
                            f.seek(start)
                            self.wfile.write(f.read(chunk_size))
                    except PermissionError as e:
                        print(f"Permission denied accessing file {file_path}: {e}")
                        self.send_error(403, "Permission denied")
                    except IOError as e:
                        print(f"IO error reading file {file_path}: {e}")
                        self.send_error(500, "Error reading file")
                    except Exception as e:
                        print(f"Error serving video file {file_path}: {e}")
                        self.send_error(500, "Error serving video file")
                    return
                else:
                    # No Range header, send the whole file
                    self.send_response(200)
                    self.send_header('Content-type', mime_type)
                    self.send_header('Accept-Ranges', 'bytes')
                    self.send_header('Content-Length', str(file_size))
                    self.send_header('Cache-Control', 'no-cache')
                    # Do NOT set Content-Disposition for streaming
                    self.end_headers()
                    try:
                        with open(file_path, 'rb') as f:
                            self.wfile.write(f.read())
                    except PermissionError as e:
                        print(f"Permission denied accessing file {file_path}: {e}")
                        self.send_error(403, "Permission denied")
                    except IOError as e:
                        print(f"IO error reading file {file_path}: {e}")
                        self.send_error(500, "Error reading file")
                    except Exception as e:
                        print(f"Error serving video file {file_path}: {e}")
                        self.send_error(500, "Error serving video file")
                    return
            else:
                # File not found - provide detailed error message
                print(f"File not found: {file_path}")
                print(f"BASE_PATH: {os.path.abspath(FILE_PATH)}")
                print(f"REL_PATH: {rel_path}")
                self.send_error(404, f"File not found: {decoded_path}")
                return

        # Handle normal file requests
        super().do_GET()
def main():
    port = 8001
    try:
        print("Attempting to start server...")
        # Get local IP address for LAN access
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            local_ip = "localhost"
        print(f"Server started at:")
        print(f"  Local:   http://127.0.0.1:{port}")
        print(f"  Network: http://{local_ip}:{port}")
        print("Access this address from other devices on your network.")
        with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except OSError as e:
        print(f"OSError occurred: {e}")
        if e.errno == 98 or e.errno == 10048:  # Address already in use
            print(f"\n❌ Error: Port {port} is already in use!")
            print("Try one of these solutions:")
            print("1. Change the port in the script (edit the 'port' variable)")
            print("2. Kill the process using the port:")
            print(f"   netstat -ano | findstr :{port}")
            print("   taskkill /PID <PID> /F")
            print("3. Wait a few minutes for the port to be released")
        else:
            print(f"Error starting server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped by admin.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()