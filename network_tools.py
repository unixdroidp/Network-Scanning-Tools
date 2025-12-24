import subprocess
import socket
import urllib.request
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import os
import sqlite3
import datetime

def check_firewall():
    try:
        result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles'], capture_output=True, text=True)
        if 'State                                 ON' in result.stdout:
            return "Firewall is ON"
        else:
            return "Firewall is OFF or Unknown"
    except Exception as e:
        return f"Unable to check firewall: {str(e)}"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        return f"Unable to get local IP: {str(e)}"

def get_public_ip():
    try:
        response = urllib.request.urlopen('https://api.ipify.org')
        ip = response.read().decode('utf-8')
        return ip
    except Exception as e:
        return f"Unable to fetch public IP: {str(e)}"

def ping_host(host):
    try:
        result = subprocess.run(['ping', '-n', '4', host], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error pinging host: {str(e)}"

def check_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, int(port)))
        sock.close()
        if result == 0:
            return f"Port {port} on {host} is open"
        else:
            return f"Port {port} on {host} is closed"
    except Exception as e:
        return f"Error checking port: {str(e)}"

def show_firewall():
    result = check_firewall()
    if "OFF" in result:
        response = messagebox.askyesno("Firewall Status", f"{result}\n\nDo you want to enable the firewall?")
        if response:
            enable_firewall()
            messagebox.showinfo("Firewall", "Firewall enabled successfully!")
        else:
            messagebox.showinfo("Firewall Status", result + "\n\nUsage: Windows Firewall protects your PC from unauthorized access.")
    else:
        response = messagebox.askyesno("Firewall Status", f"{result}\n\nDo you want to disable the firewall?")
        if response:
            disable_firewall()
            messagebox.showinfo("Firewall", "Firewall disabled successfully!")
        else:
            messagebox.showinfo("Firewall Status", result + "\n\nUsage: Windows Firewall protects your PC from unauthorized access.")

def enable_firewall():
    try:
        subprocess.run(['netsh', 'advfirewall', 'set', 'allprofiles', 'state', 'on'], check=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to enable firewall: {str(e)}")

def disable_firewall():
    try:
        subprocess.run(['netsh', 'advfirewall', 'set', 'allprofiles', 'state', 'off'], check=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to disable firewall: {str(e)}")

def show_local_ip():
    result = get_local_ip()
    messagebox.showinfo("Local IP", f"Local IP: {result}\n\nUsage: This is your device's IP address on the local network.")

def show_public_ip():
    result = get_public_ip()
    messagebox.showinfo("Public IP", f"Public IP: {result}\n\nUsage: This is your public IP visible to the internet.")

def show_ping():
    host = simpledialog.askstring("Ping Host", "Enter host to ping:")
    if host:
        result = ping_host(host)
        messagebox.showinfo("Ping Result", f"{result}\n\nUsage: Ping tests connectivity to a host by sending packets.")

def show_check_port():
    host = simpledialog.askstring("Check Port", "Enter host:")
    if host:
        port = simpledialog.askstring("Check Port", "Enter port:")
        if port:
            result = check_port(host, port)
            messagebox.showinfo("Port Check", f"{result}\n\nUsage: Checks if a specific port is open on the host.")

def show_dns_lookup():
    domain = simpledialog.askstring("DNS Lookup", "Enter domain name:")
    if domain:
        try:
            ip = socket.gethostbyname(domain)
            messagebox.showinfo("DNS Lookup", f"{domain} resolves to {ip}\n\nUsage: DNS lookup finds the IP address for a domain name.")
        except Exception as e:
            messagebox.showerror("Error", f"DNS lookup failed: {str(e)}\n\nUsage: Ensure the domain is valid.")

def show_traceroute():
    host = simpledialog.askstring("Traceroute", "Enter host:")
    if host:
        try:
            result = subprocess.run(['tracert', '-d', '-h', '10', host], capture_output=True, text=True)
            messagebox.showinfo("Traceroute", f"{result.stdout}\n\nUsage: Traceroute shows the path packets take to reach the host.")
        except Exception as e:
            messagebox.showerror("Error", f"Traceroute failed: {str(e)}\n\nUsage: Host must be reachable.")

def show_website_status():
    url = simpledialog.askstring("Website Status", "Enter URL (e.g., https://example.com):")
    if url:
        try:
            if not url.startswith('http'):
                url = 'http://' + url
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req)
            messagebox.showinfo("Website Status", f"{url} is up (Status: {response.getcode()})\n\nUsage: Checks if a website is accessible.")
        except Exception as e:
            messagebox.showerror("Error", f"Website check failed: {str(e)}\n\nUsage: Ensure URL is correct.")

def get_chrome_history():
    history_path = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data\Default\History"
    if not os.path.exists(history_path):
        return "Chrome history file not found. Make sure Chrome is installed and has history."
    try:
        # Copy the file to avoid locking issues
        import shutil
        temp_path = os.path.join(os.environ['TEMP'], 'chrome_history.db')
        shutil.copy2(history_path, temp_path)
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 100")
        results = cursor.fetchall()
        conn.close()
        os.remove(temp_path)
        if not results:
            return "No history found."
        def chrome_time_to_datetime(chrome_time):
            return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=chrome_time)
        history = "\n".join([f"{chrome_time_to_datetime(time).strftime('%Y-%m-%d %H:%M:%S')} - {title or 'No Title'}: {url} (Visits: {count})" for url, title, count, time in results])
        return history
    except Exception as e:
        return f"Error accessing history: {str(e)}"

def show_browser_history():
    history = get_chrome_history()
    # Create a scrollable window for history
    history_window = tk.Toplevel()
    history_window.title("Browser History")
    history_window.geometry("800x600")  # Larger size
    history_window.configure(bg='black')
    
    # Add delete button
    delete_btn = tk.Button(history_window, text="Delete All History", command=lambda: delete_history(history_window), bg='red', fg='white', font=("Arial", 10, "bold"))
    delete_btn.pack(pady=10)
    
    text = tk.Text(history_window, wrap=tk.WORD, font=("Arial", 10, "bold"), bg='black', fg='red', insertbackground='red')
    scrollbar = tk.Scrollbar(history_window, command=text.yview, bg='black', troughcolor='black')
    text.config(yscrollcommand=scrollbar.set)
    text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text.insert(tk.END, history)
    text.config(state=tk.DISABLED)  # Make it read-only

def delete_history(window):
    response = messagebox.askyesno("Delete History", "This will delete all Chrome browsing history. Are you sure? (Chrome must be closed)")
    if response:
        try:
            history_path = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data\Default\History"
            if os.path.exists(history_path):
                os.remove(history_path)
                messagebox.showinfo("Success", "History deleted. Restart Chrome to see changes.")
                window.destroy()
            else:
                messagebox.showerror("Error", "History file not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete history: {str(e)}")

def main():
    root = tk.Tk()
    root.title("Network Scanning Tools - Professional Edition")
    root.geometry("500x600")
    root.resizable(False, False)
    root.configure(bg='black')

    # Title
    title_label = tk.Label(root, text="Network Scanning Tools", font=("Arial", 16, "bold"), bg='black', fg='red')
    title_label.pack(pady=20)

    # Subtitle
    subtitle_label = tk.Label(root, text="Select a tool to get started", font=("Arial", 10, "bold"), bg='black', fg='white')
    subtitle_label.pack(pady=(0, 20))

    # Frame for buttons
    frame = tk.Frame(root, bg='black')
    frame.pack(pady=10)

    # Buttons with ttk for better look
    style = ttk.Style()
    style.configure("TButton", font=("Arial", 10, "bold"), padding=10, foreground='red', background='black')
    style.map("TButton", background=[('active', 'darkred'), ('pressed', 'red')])  # Hover effect

    buttons = [
        ("🔥 Check Firewall Status", show_firewall),
        ("🏠 Get Local IP Address", show_local_ip),
        ("🌐 Get Public IP Address", show_public_ip),
        ("📡 Ping a Host", show_ping),
        ("🔍 Check if Port is Open", show_check_port),
        ("🔎 DNS Lookup", show_dns_lookup),
        ("🗺️ Traceroute", show_traceroute),
        ("🌍 Check Website Status", show_website_status),
        ("📚 Browser History", show_browser_history),
        ("❌ Exit", root.quit)
    ]

    for i, (text, command) in enumerate(buttons):
        row = i // 2
        col = i % 2
        ttk.Button(frame, text=text, command=command).grid(row=row, column=col, padx=10, pady=5, sticky='ew')

    # Footer
    footer_label = tk.Label(root, text="Built with Unixdroid", font=("Arial", 8, "bold"), bg='black', fg='white')
    footer_label.pack(side='bottom', pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()