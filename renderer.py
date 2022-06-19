from PIL import Image
import requests
from io import BytesIO

UI_AVATAR_API_URL = 'https://ui-avatars.com/api/?'

def make_photo(size=64, name=None, url=None):
	if url:
		URL = url
	else:
		if not name:
			raise ValueError('User does not have name and special avatar url.')

		params = [f'name={"+".join(name.split(" "))}', 'background=random', f'size={min(max(16, size), 512)}']
		URL = UI_AVATAR_API_URL + '&'.join(params)

	response = requests.get(URL)
	assert response.status_code == 200, f"Url response code, image expected from is {response.status_code}."
	img = Image.open(BytesIO(response.content))

	if url:
		img.thumbnail((size, size), Image.ANTIALIAS)

	img.save('res.png')