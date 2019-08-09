from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from flask import abort	
from flask import request
import requests
import json
import unicodedata
from apiclient import errors
from apiclient.http import MediaFileUpload
from flask import render_template
from flask import Flask 
app = Flask(__name__) 

SCOPES = ['https://www.googleapis.com/auth/drive']

creds = '' 

def main(): # Implements the Google sign in
	global creds
	creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token: 
			creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

@app.route('/home')
def home():
	page_token = None
	global service	

	drive_query = service.files().list(q="mimeType='application/vnd.google-apps.document' and trashed = False",
		fields="nextPageToken, files(id, name)",pageToken=page_token).execute()
	files_list = drive_query.get('files', [])
	# Gets the list of docs from Google Drive
	resulting_list = ''
	if not files_list:	
		return 'No files found.'
	else:
		for file in files_list:
			resulting_list += '<li>' + u'{0} ({1})'.format(file['name'], file['id']) + '</li>'
		return resulting_list # Returns a list of all file names and IDs

		page_token = response.get('nextPageToken', None)
		if page_token is None:
			pass
		
		
@app.route('/search-in-doc/<id>', methods=['GET'])
def search(id):

	page_token = None

	if request.method == 'GET':
		if request.args.get('word', '')== '':
			return 'Error - Enter the parameters correctly'

		original_keyword = request.args.get('word', '')
		# Gets the keyword passed as parameter
		keyword = original_keyword.encode('ascii')
		# Gets the string passed as parameter and formats it as ascii
		drive_query = service.files().export(fileId=id, mimeType="text/plain").execute()
		# Exports requested file as plain text
		if keyword in drive_query: # Searches for the keyword in the file
			return 'Keyword found in requested file'
		else:
			return 'HTTP/1.1" 404'
			abort(404) # If keyword not found returns status 404	

@app.errorhandler(400)
def bad_request(error):
    # Handles error 404
    abort(404)


@app.route('/create', methods=['POST'])
def create():

	global service
	if request.method == 'POST':

		file_content = request.json['description']
		file_name = request.json['name']
		
		archivo = open('File', 'w+')	
		archivo.write(file_content)
		archivo.close()
		# Wites the content of the 'description' field in the posted json into a file 

		file_metadata = {'name': file_name , 'mimeType': 'application/vnd.google-apps.document' }
		# file_metadata is a json that contains the metadata that de created file will have in drive
		media = MediaFileUpload('File', mimetype='text/plain')
		# media describes the file that will be uploaded
		drive_query = service.files().create(body=file_metadata, media_body=media).execute()
		# Uploads the file that was writen with the content of the posted json to drive
		
		return '{"id":"' + drive_query.get('id') + '", "titulo":"' + drive_query.get('name') + '", "descripcion":"' + file_content + '"}'
		# Returns a json with the file properties


main() # App starts here
	
service = build('drive', 'v3', credentials=creds) # Used for conections with the drive API

if __name__ == '__main__':
			app.debug = True
			app.run(host='0.0.0.0',port='5000') 