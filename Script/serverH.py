from http.server import HTTPServer, BaseHTTPRequestHandler
from multipart import MultipartParser
import os
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIHandler(BaseHTTPRequestHandler):
	def set_cors_headers(self):
		"""Set CORS headers for all responses."""
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
		self.send_header('Access-Control-Allow-Headers', 'Content-Type')

	def do_GET(self):
		"""Handle GET requests for /index.html, /new_index.html, and /fastafinder."""
		if self.path == '/index.html':
			try:
				# Path to index.html in /wD
				html_file_path = '/wD/page/index.html'
				if not os.path.exists(html_file_path):
					self.send_response(404)
					self.set_cors_headers()
					self.send_header('Content-Type', 'text/plain')
					self.send_header('Connection', 'close')
					self.end_headers()
					self.wfile.write(b'index.html not found')
					return

				self.send_response(200)
				self.set_cors_headers()
				self.send_header('Content-Type', 'text/html')
				self.send_header('Connection', 'close')
				self.end_headers()
				try:
					with open(html_file_path, 'rb') as f:
						self.wfile.write(f.read())
				except BrokenPipeError:
					logger.warning("Client disconnected while sending index.html response")
					return
			except Exception as e:
				self.send_response(500)
				self.set_cors_headers()
				self.send_header('Content-Type', 'text/plain')
				self.send_header('Connection', 'close')
				try:
					self.end_headers()
					self.wfile.write(f"Server error: {str(e)}".encode())
				except BrokenPipeError:
					logger.warning("Client disconnected while sending error response for index.html")
					return
		elif self.path == '/home':
			try:
				# Path to new_index.html in /wD
				html_file_path = '/wD/page/index.html'
				if not os.path.exists(html_file_path):
					self.send_response(404)
					self.set_cors_headers()
					self.send_header('Content-Type', 'text/plain')
					self.send_header('Connection', 'close')
					self.end_headers()
					self.wfile.write(b'index.html not found')
					return

				self.send_response(200)
				self.set_cors_headers()
				self.send_header('Content-Type', 'text/html')
				self.send_header('Connection', 'close')
				self.end_headers()
				try:
					with open(html_file_path, 'rb') as f:
						self.wfile.write(f.read())
				except BrokenPipeError:
					logger.warning("Client disconnected while sending new_index.html response")
					return
			except Exception as e:
				self.send_response(500)
				self.set_cors_headers()
				self.send_header('Content-Type', 'text/plain')
				self.send_header('Connection', 'close')
				try:
					self.end_headers()
					self.wfile.write(f"Server error: {str(e)}".encode())
				except BrokenPipeError:
					logger.warning("Client disconnected while sending error response for new_index.html")
					return
		elif self.path == '/fastafinder':
			try:
				# Path to fastafinder.html in /wD/page
				html_file_path = '/wD/page/fastafinder.html'
				if not os.path.exists(html_file_path):
					self.send_response(404)
					self.set_cors_headers()
					self.send_header('Content-Type', 'text/plain')
					self.send_header('Connection', 'close')
					self.end_headers()
					self.wfile.write(b'fastafinder.html not found')
					return

				self.send_response(200)
				self.set_cors_headers()
				self.send_header('Content-Type', 'text/html')
				self.send_header('Connection', 'close')
				self.end_headers()
				try:
					with open(html_file_path, 'rb') as f:
						self.wfile.write(f.read())
				except BrokenPipeError:
					logger.warning("Client disconnected while sending fastafinder.html response")
					return
			except Exception as e:
				self.send_response(500)
				self.set_cors_headers()
				self.send_header('Content-Type', 'text/plain')
				self.send_header('Connection', 'close')
				try:
					self.end_headers()
					self.wfile.write(f"Server error: {str(e)}".encode())
				except BrokenPipeError:
					logger.warning("Client disconnected while sending error response for fastafinder.html")
					return
		else:
			self.send_response(404)
			self.set_cors_headers()
			self.send_header('Content-Type', 'text/plain')
			self.send_header('Connection', 'close')
			self.end_headers()
			self.wfile.write(b'Endpoint not found')

	def do_OPTIONS(self):
		"""Handle CORS preflight requests."""
		self.send_response(200)
		self.set_cors_headers()
		self.send_header('Connection', 'close')
		self.end_headers()

	def do_POST(self):
		# Ensure directories exist
		os.makedirs('/tmp/uploads', exist_ok=True)
		os.makedirs('/tmp/output', exist_ok=True)

		if self.path == '/generate-svg':
			try:
				# Get Content-Length and Content-Type headers
				content_length = int(self.headers.get('Content-Length', 0))
				content_type = self.headers.get('Content-Type', '')

				if 'multipart/form-data' not in content_type:
					self.send_response(400)
					self.set_cors_headers()
					self.send_header('Content-Type', 'text/plain')
					self.send_header('Connection', 'close')
					self.end_headers()
					self.wfile.write(b'Invalid Content-Type, expected multipart/form-data')
					return

				# Extract boundary from Content-Type
				boundary = content_type.split('boundary=')[1].split(';')[0].encode()

				# Parse multipart/form-data
				parser = MultipartParser(self.rfile, boundary, content_length=content_length)
				form = {}
				for part in parser:
					if part.name == 'file' and part.filename:
						form['file'] = part
					elif part.name == 'grep':
						form['grep'] = part.value

				if 'file' not in form or not form['file'].file:
					self.send_response(400)
					self.set_cors_headers()
					self.send_header('Content-Type', 'text/plain')
					self.send_header('Connection', 'close')
					self.end_headers()
					self.wfile.write(b'No file uploaded')
					return

				# Save uploaded file
				upload_file = f"/tmp/uploads/upload_{os.getpid()}.txt"
				output_svg = f"/tmp/output/output_{os.getpid()}.svg"
				with open(upload_file, 'wb') as f:
					f.write(form['file'].file.read())

				# Generate SVG
				blastCall = f"bash /wD/Script/DockerBlastCall.sh {upload_file} | bash /wD/Script/DockBlastOut2MapInputGen.sh ;python3 /wD/occurrences_map_geopandas.py;mv /wD/occurrences_map.svg {output_svg}"
				subprocess.run(blastCall, shell=True)

				# Send SVG response
				if os.path.exists(output_svg):
					self.send_response(200)
					self.set_cors_headers()
					self.send_header('Content-Type', 'image/svg+xml')
					self.send_header('Connection', 'close')
					self.end_headers()
					try:
						with open(output_svg, 'rb') as f:
							self.wfile.write(f.read())
					except BrokenPipeError:
						logger.warning("Client disconnected while sending SVG response")
						return
					# Clean up
					os.remove(upload_file)
					os.remove(output_svg)
				else:
					self.send_response(500)
					self.set_cors_headers()
					self.send_header('Content-Type', 'text/plain')
					self.send_header('Connection', 'close')
					self.end_headers()
					self.wfile.write(b'Failed to generate SVG')
			except Exception as e:
				self.send_response(500)
				self.set_cors_headers()
				self.send_header('Content-Type', 'text/plain')
				self.send_header('Connection', 'close')
				try:
					self.end_headers()
					self.wfile.write(f"Server error: {str(e)}".encode())
				except BrokenPipeError:
					logger.warning("Client disconnected while sending error response for SVG")
					return

		elif self.path == '/generate-html':
			try:
				# Get Content-Length and Content-Type headers
				content_length = int(self.headers.get('Content-Length', 0))
				content_type = self.headers.get('Content-Type', '')

				if 'multipart/form-data' not in content_type:
					self.send_response(400)
					self.set_cors_headers()
					self.send_header('Content-Type', 'text/plain')
					self.send_header('Connection', 'close')
					self.end_headers()
					self.wfile.write(b'Invalid Content-Type, expected multipart/form-data')
					return

				# Extract boundary from Content-Type
				boundary = content_type.split('boundary=')[1].split(';')[0].encode()

				# Parse multipart/form-data
				parser = MultipartParser(self.rfile, boundary, content_length=content_length)
				form = {}
				for part in parser:
					if part.name == 'file' and part.filename:
						form['file'] = part
					elif part.name == 'grep':
						form['grep'] = part.value

				if 'file' not in form or not form['file'].file:
					self.send_response(400)
					self.set_cors_headers()
					self.send_header('Content-Type', 'text/plain')
					self.send_header('Connection', 'close')
					self.end_headers()
					self.wfile.write(b'No file uploaded')
					return

				# Save uploaded file
				upload_file = f"/tmp/uploads/upload_{os.getpid()}.txt"
				output_svg = f"/tmp/output/output_{os.getpid()}.svg"
				with open(upload_file, 'wb') as f:
					f.write(form['file'].file.read())

				# Generate SVG
				blastCall = f"bash /wD/Script/DockerBlastCall.sh {upload_file} | bash /wD/Script/DockBlastOut2MapInputGen.sh ;python3 /wD/occurrences_map_geopandas.py;mv /wD/occurrences_map.svg {output_svg}"
				subprocess.run(blastCall, shell=True)

				# Send HTML response with embedded SVG
				if os.path.exists(output_svg):
					self.send_response(200)
					self.set_cors_headers()
					self.send_header('Content-Type', 'text/html')
					self.send_header('Connection', 'close')
					self.end_headers()
					try:
						with open(output_svg, 'r') as f:
							svg_content = f.read()
						html_content = f"""
						<!DOCTYPE html>
						<html lang="en">
						<head>
							<meta charset="UTF-8">
							<meta name="viewport" content="width=device-width, initial-scale=1.0">
							<title>Generated SVG</title>
							<style>
								body {{ display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f0f0f0; }}
								svg {{ max-width: 100%; max-height: 100%; }}
							</style>
						</head>
						<body>
							{svg_content}
						</body>
						</html>
						"""
						self.wfile.write(html_content.encode())
					except BrokenPipeError:
						logger.warning("Client disconnected while sending HTML response")
						return
					# Clean up
					os.remove(upload_file)
					os.remove(output_svg)
				else:
					self.send_response(500)
					self.set_cors_headers()
					self.send_header('Content-Type', 'text/plain')
					self.send_header('Connection', 'close')
					self.end_headers()
					self.wfile.write(b'Failed to generate SVG')
			except Exception as e:
				self.send_response(500)
				self.set_cors_headers()
				self.send_header('Content-Type', 'text/plain')
				self.send_header('Connection', 'close')
				try:
					self.end_headers()
					self.wfile.write(f"Server error: {str(e)}".encode())
				except BrokenPipeError:
					logger.warning("Client disconnected while sending error response for HTML")
					return

		elif self.path in ['/grep', '/grep0', '/greptitle']:
			try:
				# Get Content-Length and Content-Type headers
				content_length = int(self.headers.get('Content-Length', 0))
				content_type = self.headers.get('Content-Type', '')

				if 'multipart/form-data' not in content_type:
					self.send_response(400)
					self.set_cors_headers()
					self.send_header('Content-Type', 'text/plain')
					self.send_header('Connection', 'close')
					self.end_headers()
					self.wfile.write(b'Invalid Content-Type, expected multipart/form-data')
					return

				# Extract boundary from Content-Type
				boundary = content_type.split('boundary=')[1].split(';')[0].encode()

				# Parse multipart/form-data
				parser = MultipartParser(self.rfile, boundary, content_length=content_length)
				form = {}
				for part in parser:
					if part.name == 'file' and part.filename:
						form['file'] = part
					elif part.name == 'grep':
						form['grep'] = part.value
					elif part.name == 'num':
						form['num'] = part.value

				if 'file' not in form or not form['file'].file:
					self.send_response(400)
					self.set_cors_headers()
					self.send_header('Content-Type', 'text/plain')
					self.send_header('Connection', 'close')
					self.end_headers()
					self.wfile.write(b'No file uploaded')
					return
				if 'grep' not in form:
					self.send_response(400)
					self.set_cors_headers()
					self.send_header('Content-Type', 'text/plain')
					self.send_header('Connection', 'close')
					self.end_headers()
					self.wfile.write(b'No grep parameter provided')
					return

				# Save uploaded file
				upload_file = f"/tmp/uploads/upload_{os.getpid()}.txt"
				output_txt = f"/tmp/output/output_{os.getpid()}.txt"
				with open(upload_file, 'wb') as f:
					f.write(form['file'].file.read())

				# Run grep command with the provided grep parameter
				grep_param = form['grep']
				num_param = form.get('num', '1')  # Default to 1 if num is not provided

				if self.path == '/grep0':
					subprocess.run(
						f"""(echo "ID\t'{grep_param}'\tT3\tT4\tT5\tT6\tT7\tT8\tT9\tT10\tT11\tT12" ;grep -m 1 '{grep_param}</OSLT>' -B 40 /wD/Metadata.xml | grep -e '<CreateDate>' -e '<Extra>' -e '<SubName>' -e '<Title>' -e '<SubType>' | head -n 5 )| sh /wD/blastn2jsonSTDIN.sh | tr -d '\\' > {output_txt}""",
						shell=True
					)
				elif self.path == '/greptitle':
					subprocess.run(
						f"""grep -m '{num_param}' '{grep_param}</Title>' -B 40 /wD/Metadata.xml | grep -e '<CreateDate>' -e '<Extra>' -e '<SubName>' -e '<Title>' -e '<SubType>' > {output_txt}""",
						shell=True
					)
				else:
					subprocess.run(
						f"""grep -m 1 '{grep_param}</OSLT>' -B 41 /wD/Metadata.xml | grep -e '<CreateDate>' -e '<Extra>' -e '<SubName>' -e '<Title>' -e '<SubType>' | head -n 5 > {output_txt}""",
						shell=True
					)

				# Send text response
				if os.path.exists(output_txt):
					self.send_response(200)
					self.set_cors_headers()
					self.send_header('Content-Type', 'text/plain')
					self.send_header('Connection', 'close')
					self.end_headers()
					try:
						with open(output_txt, 'rb') as f:
							self.wfile.write(f.read())
					except BrokenPipeError:
						logger.warning("Client disconnected while sending grep response")
						return
					# Clean up
					os.remove(upload_file)
					os.remove(output_txt)
				else:
					self.send_response(500)
					self.set_cors_headers()
					self.send_header('Content-Type', 'text/plain')
					self.send_header('Connection', 'close')
					self.end_headers()
					self.wfile.write(b'Failed to grep Metadata.xml')
			except Exception as e:
				self.send_response(500)
				self.set_cors_headers()
				self.send_header('Content-Type', 'text/plain')
				self.send_header('Connection', 'close')
				try:
					self.end_headers()
					self.wfile.write(f"Server error: {str(e)}".encode())
				except BrokenPipeError:
					logger.warning("Client disconnected while sending error response for grep")
					return

		else:
			self.send_response(404)
			self.set_cors_headers()
			self.send_header('Content-Type', 'text/plain')
			self.send_header('Connection', 'close')
			self.end_headers()
			self.wfile.write(b'Endpoint not found')

if __name__ == '__main__':
	server = HTTPServer(('0.0.0.0', 8080), APIHandler)
	logger.info("Starting server on port 8080...")
	server.serve_forever()
