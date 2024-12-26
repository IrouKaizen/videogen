from http.server import SimpleHTTPRequestHandler, HTTPServer
import os

# Change directory to the folder containing your HTML, CSS, and JS files

os.chdir(r'C:/Users/Administrateur.OTR-2018-503/Automated_videogen/Interface')

# Set up the server
server_address = ('', 8000)  # Serveur sur localhost, port 8000
httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)

print("Server running on http://localhost:8000")
httpd.serve_forever()
