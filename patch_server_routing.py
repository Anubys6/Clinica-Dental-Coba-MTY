import os

server_path = r'C:\Users\SAmue\.gemini\antigravity\scratch\clinica-dental-coba-mty\server.py'

with open(server_path, 'r', encoding='utf-8') as f:
    text = f.read()

old_block = """    def translate_path(self, path):
        clean_path = path.split('?', 1)[0].split('#', 1)[0]
        if clean_path in ('/doctor', '/doctor/', '/portal-medico', '/portal-medico/', '/portal-doctor', '/portal-doctor/', '/clinica-coba/admin', '/clinica-coba/admin/'):
            return os.path.join(BASE_DIR, 'portal_doctor.html')

        if clean_path in ('/', '/index.html', '/automatic', '/automatic/'):
            return os.path.join(AUTOMATIC_DIR, 'index.html')
        if clean_path.startswith('/automatic/'):
            rel = clean_path[len('/automatic/'):]
            return os.path.join(AUTOMATIC_DIR, rel.replace('/', os.sep))

        if clean_path in ('/styles.css', '/script.js') or clean_path.startswith('/images/scene_') or clean_path.startswith('/images/commercial_'):
            referer = self.headers.get('Referer', '')
            if '/clinica-coba' not in referer:
                return os.path.join(AUTOMATIC_DIR, clean_path.lstrip('/').replace('/', os.sep))

        if clean_path in ('/clinica-coba', '/clinica-coba/'):
            return os.path.join(BASE_DIR, 'index.html')
        if clean_path.startswith('/clinica-coba/'):
            rel = clean_path[len('/clinica-coba/'):]
            return os.path.join(BASE_DIR, rel.replace('/', os.sep))

        referer = self.headers.get('Referer', '')
        if '/clinica-coba' not in referer and clean_path.startswith('/images/'):
            candidate = os.path.join(AUTOMATIC_DIR, clean_path.lstrip('/').replace('/', os.sep))
            if os.path.exists(candidate):
                return candidate

        return super().translate_path(path)"""

new_block = """    def translate_path(self, path):
        clean_path = path.split('?', 1)[0].split('#', 1)[0]

        # Portal Médico Cobá
        if clean_path in ('/doctor', '/doctor/', '/portal-medico', '/portal-medico/', '/portal-doctor', '/portal-doctor/', '/clinica-coba/admin', '/clinica-coba/admin/'):
            return os.path.join(BASE_DIR, 'portal_doctor.html')

        # Agencia AUTOMATIC (si se solicita explícitamente)
        if clean_path in ('/automatic', '/automatic/', '/agency', '/agency/'):
            return os.path.join(AUTOMATIC_DIR, 'index.html')
        if clean_path.startswith('/automatic/'):
            rel = clean_path[len('/automatic/'):]
            return os.path.join(AUTOMATIC_DIR, rel.replace('/', os.sep))

        # Clínica Dental Cobá (predeterminado en raíz, /index.html, /coba, /clinica-coba)
        if clean_path in ('/', '/index.html', '/coba', '/coba/', '/coba.html', '/clinica-coba', '/clinica-coba/'):
            return os.path.join(BASE_DIR, 'index.html')
        if clean_path.startswith('/clinica-coba/'):
            rel = clean_path[len('/clinica-coba/'):]
            return os.path.join(BASE_DIR, rel.replace('/', os.sep))

        # Enrutamiento de imágenes comerciales si el referer es la agencia
        referer = self.headers.get('Referer', '')
        if '/automatic' in referer and clean_path.startswith('/images/'):
            candidate = os.path.join(AUTOMATIC_DIR, clean_path.lstrip('/').replace('/', os.sep))
            if os.path.exists(candidate):
                return candidate

        return super().translate_path(path)"""

if old_block in text:
    text = text.replace(old_block, new_block)
    with open(server_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('SUCCESS: server.py translate_path updated!')
else:
    print('ERROR: old_block not found in server.py')
