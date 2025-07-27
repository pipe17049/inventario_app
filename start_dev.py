#!/usr/bin/env python
"""
Development server starter
"""
import subprocess
import sys
import time
import signal
import os
from pathlib import Path

# Add Django settings
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_project.settings')

processes = []

def cleanup():
    """Clean up all processes"""
    print("\n🛑 Shutting down services...")
    for proc in processes:
        if proc.poll() is None:  # Process is still running
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    print("✅ All services stopped")

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    cleanup()
    sys.exit(0)

def main():
    # Set up signal handling
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🚀 Starting Inventory Management System...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ manage.py not found. Run this script from the project root.")
        sys.exit(1)
    
    try:
        # Start Django server
        print("📱 Starting Django API server (port 8000)...")
        django_proc = subprocess.Popen([
            sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'
        ])
        processes.append(django_proc)
        time.sleep(3)
        
        # Start WebSocket server
        print("🔌 Starting WebSocket server (port 8001)...")
        ws_proc = subprocess.Popen([
            sys.executable, 'websocket_server.py'
        ])
        processes.append(ws_proc)
        time.sleep(2)
        
        # Start frontend server
        print("🌐 Starting frontend server (port 3000)...")
        frontend_proc = subprocess.Popen([
            sys.executable, '-m', 'http.server', '3000'
        ], cwd='frontend')
        processes.append(frontend_proc)
        
        print("\n✅ All services started successfully!")
        print("\n📋 Available endpoints:")
        print("   🌐 Frontend:  http://localhost:3000")
        print("   🔧 API:       http://localhost:8000/api/")
        print("   🔌 WebSocket: ws://localhost:8001")
        print("   ⚙️  Admin:     http://localhost:8000/admin/")
        print("\n⌨️  Press Ctrl+C to stop all services")
        
        # Wait for processes
        while True:
            time.sleep(1)
            # Check if any process has died
            for proc in processes:
                if proc.poll() is not None:
                    print(f"\n⚠️  A service has stopped unexpectedly")
                    cleanup()
                    sys.exit(1)
                    
    except Exception as e:
        print(f"\n❌ Error starting services: {e}")
        cleanup()
        sys.exit(1)

if __name__ == '__main__':
    main()
