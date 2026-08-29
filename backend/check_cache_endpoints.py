import requests
import sys

BASE = 'http://127.0.0.1:5000'

def login():
    # Inspect run.cache object
    try:
        import run as runmod
        print('run.cache id=', id(runmod.cache), 'has app=', hasattr(runmod.cache, 'app'), 'cache.app=', type(getattr(runmod.cache, 'app', None)))
    except Exception as e:
        print('inspect run.cache failed', e)

    # Login uses email + password according to the auth route
    r = requests.post(BASE + '/auth/login', json={'email': 'admin@gmail.com', 'password': 'admin'})
    print('LOGIN', r.status_code)
    try:
        print(r.text)
    except Exception:
        pass
    if r.status_code != 200:
        sys.exit(1)
    js = r.json()
    token = js.get('access_token') or js.get('token') or js.get('accessToken')
    if not token:
        print('No token found in login response')
        sys.exit(1)
    return token


def call(path, token):
    headers = {'Authorization': 'Bearer ' + token}
    r = requests.get(BASE + path, headers=headers)
    print(path, r.status_code)
    print(r.text[:2000])


if __name__ == '__main__':
    token = login()
    call('/admin/stats', token)
    call('/admin/top-partners', token)
