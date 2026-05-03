"""
Build script for YouTube Downloader Pro - Full Bundling
Run: python build_exe.py
Author: 3Bhussein
GitHub: https://github.com/3Bhussein/YouTube-Downloader-Pro
"""

import PyInstaller.__main__
import os
import shutil
import subprocess

def clean_build():
    """Clean previous build files"""
    print("🧹 Cleaning previous builds...")
    
    # Kill any running instances
    try:
        subprocess.run(['taskkill', '/f', '/im', 'YouTubeDownloaderPro.exe'], 
                      capture_output=True, shell=True)
        print("   ✓ Killed running instances")
    except:
        pass
    
    # Remove folders
    for folder in ['dist', 'build']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   ✓ Removed {folder}/")
    
    # Remove spec file
    if os.path.exists('YouTubeDownloaderPro.spec'):
        os.remove('YouTubeDownloaderPro.spec')
        print("   ✓ Removed spec file")

def build_exe():
    print("="*60)
    print("🔨 Building YouTube Downloader Pro v2.0")
    print("👤 Author: 3Bhussein")
    print("📦 Packaging ALL dependencies into EXE")
    print("="*60)
    
    clean_build()
    
    # Full build options - includes everything (fixed UPX issue)
    opts = [
        'youtube_downloader.py',
        '--name=YouTubeDownloaderPro',
        '--onefile',                    # Single EXE file
        '--windowed',                   # No console window
        '--clean',                      # Clean build
        '--noconfirm',                  # No confirmation prompts
        '--hidden-import=yt_dlp',       # Include yt-dlp
        '--hidden-import=yt_dlp.extractor',
        '--hidden-import=yt_dlp.downloader',
        '--hidden-import=yt_dlp.postprocessor',
        '--hidden-import=tkinter',
        '--hidden-import=threading',
        '--hidden-import=subprocess',
        '--hidden-import=pathlib',
        '--hidden-import=re',
        '--hidden-import=json',
        '--collect-all=yt_dlp',         # Collect ALL yt-dlp files
    ]
    
    # Add icon if exists
    if os.path.exists("icon.ico"):
        opts.append('--icon=icon.ico')
        print("✅ Icon found - included")
    else:
        print("⚠️  No icon.ico found - using default")
    
    print("\n🚀 Building standalone EXE...")
    print("   This will take 2-3 minutes...")
    print("   All dependencies will be embedded inside the EXE")
    print("   Your friend won't need to install anything!\n")
    
    try:
        # Run as non-admin (removed the admin requirement)
        PyInstaller.__main__.run(opts)
        
        exe_path = os.path.abspath('dist/YouTubeDownloaderPro.exe')
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print("\n" + "="*60)
            print("✅ BUILD COMPLETE!")
            print("="*60)
            print(f"📁 EXE Location: {exe_path}")
            print(f"📦 File Size: {size_mb:.2f} MB")
            print("\n✨ What's INCLUDED in the EXE:")
            print("   • Python runtime (complete)")
            print("   • yt-dlp library (full)")
            print("   • tkinter GUI framework")
            print("   • All dependencies")
            print("   • No external requirements needed!")
            print("\n📤 You can now send this EXE to your friend")
            print("   They just double-click to run - NO INSTALLATION NEEDED!")
            print("\n🔗 GitHub: https://github.com/3Bhussein/YouTube-Downloader-Pro")
            print("="*60)
        else:
            print("\n❌ Build failed! Check for errors above.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Try the simple build command instead:")
        print('   pyinstaller --onefile --windowed --name YouTubeDownloaderPro youtube_downloader.py')

if __name__ == "__main__":
    build_exe()