#!/usr/bin/env python3

"""
Cloud Upload Test Script for Raspberry Pi

Uploads files to a remote server using HTTP POST requests

Usage:
    python3 cloud_upload_test.py /path/to/file.jpg
    python3 cloud_upload_test.py /path/to/file.jpg --server http://192.168.1.100:5001
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
DEFAULT_SERVER_URL = "https://662a630e-2600-4c96-bdad-c6c625b41c0e-00-13s949ql9aoor.janeway.replit.dev:3000"  # Replit deployment URL
# For local development: "http://localhost:5001"
DEFAULT_UPLOAD_ENDPOINT = "/api/upload"
DEFAULT_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes (CLI default)
DEFAULT_MAX_FILE_SIZE_PI_ZERO = 20 * 1024 * 1024  # 20MB for Pi Zero 2W


def check_memory(min_free_mb=100):
    """
    Check available system memory.
    
    Args:
        min_free_mb: Minimum free memory in MB to consider safe (default: 100MB)
    
    Returns:
        dict: {'available': bool, 'free_mb': int, 'warning': str or None}
    """
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            mem_available = None
            for line in meminfo.split('\n'):
                if 'MemAvailable:' in line:
                    mem_available = int(line.split()[1])  # in KB
                    break
            
            if mem_available is None:
                # Fallback to MemFree if MemAvailable not available
                for line in meminfo.split('\n'):
                    if 'MemFree:' in line:
                        mem_available = int(line.split()[1])
                        break
            
            if mem_available is not None:
                mem_available_mb = mem_available // 1024
                warning = None
                if mem_available_mb < min_free_mb:
                    warning = f"Low memory: {mem_available_mb}MB free (recommended: {min_free_mb}MB+)"
                
                return {
                    'available': mem_available_mb >= min_free_mb,
                    'free_mb': mem_available_mb,
                    'warning': warning
                }
    except Exception:
        pass
    
    # If we can't read memory info, assume it's okay
    return {
        'available': True,
        'free_mb': None,
        'warning': None
    }


def upload_file(file_path, server_url=None, endpoint=None, max_file_size=None, timeout=None, check_mem=True, verbose=True):
    """
    Upload a file to the remote server.
    
    Args:
        file_path: Path to the file to upload
        server_url: Base URL of the server (default: DEFAULT_SERVER_URL)
        endpoint: API endpoint path (default: DEFAULT_UPLOAD_ENDPOINT)
        max_file_size: Maximum file size in bytes (default: DEFAULT_MAX_FILE_SIZE)
        timeout: Upload timeout in seconds (default: 30)
        check_mem: Whether to check available memory before upload (default: True)
        verbose: Whether to print progress messages (default: True)
    
    Returns:
        dict: Response from server with status and message
    """
    if server_url is None:
        server_url = DEFAULT_SERVER_URL
    
    if endpoint is None:
        endpoint = DEFAULT_UPLOAD_ENDPOINT
    
    if max_file_size is None:
        max_file_size = DEFAULT_MAX_FILE_SIZE
    
    if timeout is None:
        timeout = 30
    
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
    if file_size > max_file_size:
        max_mb = max_file_size / (1024 * 1024)
        file_mb = file_size / (1024 * 1024)
        return {
            "success": False,
            "error": f"File too large: {file_mb:.2f}MB (max: {max_mb:.2f}MB)"
        }
    
    # Check memory if requested
    if check_mem:
        mem_check = check_memory(min_free_mb=100)
        if mem_check['warning'] and verbose:
            print(f"⚠ {mem_check['warning']}")
        if not mem_check['available']:
            return {
                "success": False,
                "error": f"Insufficient memory: {mem_check['free_mb']}MB free (need 100MB+)",
                "hint": "Free up memory or reduce file size"
            }
    
    # Upload file
    try:
        if verbose:
            file_mb = file_size / (1024 * 1024)
            print(f"Uploading {file_path.name} ({file_mb:.2f}MB)...")
            print(f"Server: {upload_url}")
        
        with open(file_path, 'rb') as f:
            # Replit format: simple filename without content-type
            files = {'file': (os.path.basename(str(file_path)), f)}
            response = requests.post(upload_url, files=files, timeout=timeout)
        
        # Check response - Replit returns JSON with success, filename, originalName, size, path
        if response.status_code == 200:
            try:
                result = response.json()
                # Replit response format: {"success": true, "filename": "...", "originalName": "...", "size": ..., "path": "..."}
                if result.get('success', True):  # Replit may or may not include 'success' field, default to True if 200
                    return {
                        "success": True,
                        "message": "Upload successful",
                        "response": result
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get('error', 'Upload failed'),
                        "response": result
                    }
            except ValueError:
                return {
                    "success": True,
                    "message": "Upload successful",
                    "response": response.text
                }
        else:
            # Try to parse error response
            try:
                error_data = response.json()
                error_msg = error_data.get('error', f"Upload failed with status {response.status_code}")
            except:
                error_msg = f"Upload failed with status {response.status_code}"
            
            return {
                "success": False,
                "error": error_msg,
                "response": response.text
            }
    
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": f"Could not connect to server: {upload_url}",
            "hint": "Check that the server is running and the URL is correct. For Replit, ensure you're using HTTPS (https://your-repl.replit.app) and the server is deployed."
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": f"Upload timed out ({timeout} seconds)",
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
  python3 cloud_upload_test.py /home/pi/pictures/image.jpg --server http://192.168.1.100:5001
  
  # List uploaded files
  python3 cloud_upload_test.py --list --server http://192.168.1.100:5001
  
  # Delete a file
  python3 cloud_upload_test.py --delete filename.jpg --server http://192.168.1.100:5001
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
    
    # Handle list command
    if args.list:
        result = list_files(args.server)
        if result["success"]:
            print("\n✓ File list retrieved successfully:")
            files = result.get("files", [])
            if isinstance(files, list):
                if files:
                    print(f"\nFound {len(files)} file(s):")
                    for f in files:
                        size_mb = f.get('size', 0) / (1024 * 1024)
                        print(f"  - {f.get('name', 'unknown')} ({size_mb:.2f} MB)")
                else:
                    print("  No files found")
            else:
                print(files)
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
            resp = result['response']
            if isinstance(resp, dict):
                print(f"  Original name: {resp.get('originalName', 'N/A')}")
                print(f"  Saved as: {resp.get('filename', 'N/A')}")
                print(f"  Size: {resp.get('size', 0)} bytes")
                print(f"  Path: {resp.get('path', 'N/A')}")
            else:
                print(f"Server response: {resp}")
    else:
        print(f"\n✗ Upload failed: {result.get('error', 'Unknown error')}")
        if "hint" in result:
            print(f"   Hint: {result['hint']}")
        sys.exit(1)


if __name__ == "__main__":
    main()

