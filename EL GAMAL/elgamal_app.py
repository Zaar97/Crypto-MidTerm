from flask import Flask, request, render_template, redirect, url_for
import random

app = Flask(__name__)

# Simpan data kartu sementara
cards_data = {}

# Fungsi untuk menghasilkan pasangan kunci ElGamal
def generate_keypair(p, g):
    x = random.randint(1, p - 2)  # Private key
    y = pow(g, x, p)  # Public key component
    return ((p, g, y), x)  # Public key, Private key

def encrypt(public_key, plaintext):
    p, g, y = public_key
    encrypted_text = []

    for char in plaintext:
        k = random.randint(1, p - 2)  # Random integer for encryption
        a = pow(g, k, p)  # First part of ciphertext
        b = (ord(char) * pow(y, k, p)) % p  # Second part of ciphertext
        encrypted_text.append((a, b))
    
    return encrypted_text

def decrypt(private_key, public_key, ciphertext):
    p, g, y = public_key
    x = private_key
    decrypted_text = ''

    for a, b in ciphertext:
        # Decrypt each character
        s = pow(a, x, p)
        inv_s = modinv(s, p)  # Modular inverse of s
        decrypted_text += chr((b * inv_s) % p)
    
    return decrypted_text

def modinv(a, m):
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

# Halaman utama (redirect ke submit card sebagai default)
@app.route('/')
def home():
    return redirect(url_for('submit_card'))

# Halaman untuk submit kartu
@app.route('/submit', methods=['GET', 'POST'])
def submit_card():
    if request.method == 'POST':
        # Ambil data dari form
        name = request.form['name']
        card_number = request.form['card_number']
        expiry_date = request.form['expiry_date']
        cvv = request.form['cvv']
        
        # Generate keypair dan encrypt data
        p = 467  # Large prime number for ElGamal
        g = 2  # Primitive root mod p
        public_key, private_key = generate_keypair(p, g)
        encrypted_card_number = encrypt(public_key, card_number)
        encrypted_expiry_date = encrypt(public_key, expiry_date)
        encrypted_cvv = encrypt(public_key, cvv)

        # Simpan data ke dictionary
        cards_data[name] = {
            'public_key': public_key,
            'private_key': private_key,
            'encrypted_data': {
                'card_number': encrypted_card_number,
                'expiry_date': encrypted_expiry_date,
                'cvv': encrypted_cvv
            }
        }

        # Redirect ke halaman submit dengan pesan sukses
        return redirect(url_for('submit_card', success='true'))

    success_message = request.args.get('success')
    return render_template('submit_card.html', success_message=success_message)

# Halaman untuk melihat daftar kartu
@app.route('/view')
def view_card():
    return render_template('view_card.html', cards_data=cards_data)

# Halaman untuk dekripsi kartu
@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt_card():
    decrypted_message = None
    if request.method == 'POST':
        # Ambil nama dan private key dari form
        name = request.form['name']
        private_key = int(request.form['private_key'])  # Private key

        if name in cards_data:
            encrypted_data = cards_data[name]['encrypted_data']
            public_key = cards_data[name]['public_key']

            # Dekripsi data
            decrypted_card_number = decrypt(private_key, public_key, encrypted_data['card_number'])
            decrypted_expiry_date = decrypt(private_key, public_key, encrypted_data['expiry_date'])
            decrypted_cvv = decrypt(private_key, public_key, encrypted_data['cvv'])

            decrypted_message = {
                'card_number': decrypted_card_number,
                'expiry_date': decrypted_expiry_date,
                'cvv': decrypted_cvv
            }

    return render_template('decrypt_card.html', decrypted_message=decrypted_message)

if __name__ == "__main__":
    app.run(debug=True)
