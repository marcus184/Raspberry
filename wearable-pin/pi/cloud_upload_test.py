#!/usr/bin/env python3
"""
Cloud Upload Test Script for Raspberry Pi
Uploads files to a remote server using HTTP POST requests

Usage:
    python3 cloud_upload_test.py /path/to/file.jpg
    python3 cloud_upload_test.py /path/to/file.jpg --server http://192.168.1.100:3000
"""

import sys
import os
import argparse
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Error: requests library not available.")
    print("Install with: pip install requests")
    print("Or on Raspberry Pi: sudo pip3 install requests")
    sys.exit(1)


# Default server configuration
DEFAULT_SERVER_URL = "http://YOUR_SERVER_IP:3000"
DEFAULT_UPLOAD_ENDPOINT = "/api/upload"
DEFAULT_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes


def upload_file(file_path, server_url=None, endpoint=None):
    """
    Upload a file to the remote server.
    
    Args:
        file_path: Path to the file to upload
        server_url: Base URL of the server (default: DEFAULT_SERVER_URL)
        endpoint: API endpoint path (default: DEFAULT_UPLOAD_ENDPOINT)
    
    Returns:
        dict: Response from server with status and message
    """
    if server_url is None:
        server_url = DEFAULT_SERVER_URL
    
    if endpoint is None:
        endpoint = DEFAULT_UPLOAD_ENDPOINT
    
    # Construct full URL
    upload_url = f"{server_url.rstrip('/')}{endpoint}"
    
    # Validate file exists
    file_path = Path(file_path)
    if not file_path.exists():
        return {
            "success": False,
            "error": f"File not found: {file_path}"
        }
    
    # Check file size
    file_size = file_path.stat().st_size
    if file_size > DEFAULT_MAX_FILE_SIZE:
        return {
            "success": False,
            "error": f"File too large: {file_size} bytes (max: {DEFAULT_MAX_FILE_SIZE} bytes)"
        }
    
    # Upload file
    try:
        print(f"Uploading {file_path.name} ({file_size} bytes)...")
        print(f"Server: {upload_url}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/octet-stream')}
            response = requests.post(upload_url, files=files, timeout=30)
        
        # Check response
        if response.status_code == 200:
            try:
                result = response.json()
                return {
                    "success": True,
                    "message": "Upload successful",
                    "response": result
                }
            except ValueError:
                return {
                    "success": True,
                    "message": "Upload successful",
                    "response": response.text
                }
        else:
            return {
                "success": False,
                "error": f"Upload failed with status {response.status_code}",
                "response": response.text
            }
    
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": f"Could not connect to server: {upload_url}",
            "hint": "Check that the server is running and the URL is correct"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Upload timed out (30 seconds)",
            "hint": "Check network connection and file size"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Upload error: {str(e)}"
        }


def list_files(server_url=None, endpoint=None):
    """
    Get list of uploaded files from the server.
    
    Args:
        server_url: Base URL of the server (default: DEFAULT_SERVER_URL)
        endpoint: API endpoint path (default: "/api/files")
    
    Returns:
        dict: Response from server with file list
    """
    if server_url is None:
        server_url = DEFAULT_SERVER_URL
    
    if endpoint is None:
        endpoint = "/api/files"
    
    list_url = f"{server_url.rstrip('/')}{endpoint}"
    
    try:
        print(f"Fetching file list from: {list_url}")
        response = requests.get(list_url, timeout=10)
        
        if response.status_code == 200:
            try:
                files = response.json()
                return {
                    "success": True,
                    "files": files
                }
            except ValueError:
                return {
                    "success": True,
                    "files": response.text
                }
        else:
            return {
                "success": False,
                "error": f"Failed to get file list: status {response.status_code}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching file list: {str(e)}"
        }


def delete_file(filename, server_url=None, endpoint=None):
    """
    Delete a file from the server.
    
    Args:
        filename: Name of the file to delete
        server_url: Base URL of the server (default: DEFAULT_SERVER_URL)
        endpoint: API endpoint path (default: "/api/files/{filename}")
    
    Returns:
        dict: Response from server
    """
    if server_url is None:
        server_url = DEFAULT_SERVER_URL
    
    if endpoint is None:
        endpoint = f"/api/files/{filename}"
    
    delete_url = f"{server_url.rstrip('/')}{endpoint}"
    
    try:
        print(f"Deleting file: {filename}")
        print(f"Server: {delete_url}")
        response = requests.delete(delete_url, timeout=10)
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": f"File {filename} deleted successfully"
            }
        else:
            return {
                "success": False,
                "error": f"Delete failed with status {response.status_code}",
                "response": response.text
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Delete error: {str(e)}"
        }


def main():
    """Main function to handle command-line arguments and execute upload."""
    parser = argparse.ArgumentParser(
        description="Upload files from Raspberry Pi to cloud server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload a single file
  python3 cloud_upload_test.py /home/pi/pictures/image.jpg --server http://192.168.1.100:3000
  
  # List uploaded files
  python3 cloud_upload_test.py --list --server http://192.168.1.100:3000
  
  # Delete a file
  python3 cloud_upload_test.py --delete filename.jpg --server http://192.168.1.100:3000
        """
    )
    
    parser.add_argument(
        'file_path',
        nargs='?',
        help='Path to the file to upload'
    )
    
    parser.add_argument(
        '--server',
        default=DEFAULT_SERVER_URL,
        help=f'Server URL (default: {DEFAULT_SERVER_URL})'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all uploaded files on the server'
    )
    
    parser.add_argument(
        '--delete',
        metavar='FILENAME',
        help='Delete a file from the server by filename'
    )
    
    args = parser.parse_args()
    
    # Check if server URL is still default
    if args.server == DEFAULT_SERVER_URL:
        print("⚠ Warning: Using default server URL. Please set --server option.")
        print(f"   Example: --server http://192.168.1.100:3000")
        print()
    
    # Handle list command
    if args.list:
        result = list_files(args.server)
        if result["success"]:
            print("\n✓ File list retrieved successfully:")
            print(result.get("files", "No files found"))
        else:
            print(f"\n✗ Error: {result.get('error', 'Unknown error')}")
        return
    
    # Handle delete command
    if args.delete:
        result = delete_file(args.delete, args.server)
        if result["success"]:
            print(f"\n✓ {result.get('message', 'File deleted')}")
        else:
            print(f"\n✗ Error: {result.get('error', 'Unknown error')}")
        return
    
    # Handle upload command
    if not args.file_path:
        parser.print_help()
        print("\nError: Please provide a file path to upload")
        sys.exit(1)
    
    result = upload_file(args.file_path, args.server)
    
    if result["success"]:
        print(f"\n✓ {result.get('message', 'Upload successful')}")
        if "response" in result:
            print(f"Server response: {result['response']}")
    else:
        print(f"\n✗ Upload failed: {result.get('error', 'Unknown error')}")
        if "hint" in result:
            print(f"   Hint: {result['hint']}")
        sys.exit(1)


if __name__ == "__main__":
    main()

