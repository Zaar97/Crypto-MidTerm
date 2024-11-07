from flask import Flask, request, render_template, redirect, url_for
import random

app = Flask(__name__)

# Simpan data kartu sementara
cards_data = {}

# Fungsi untuk menghasilkan pasangan kunci RSA
def generate_keypair(p, q):
    n = p * q
    phi = (p - 1) * (q - 1)

    e = random.randrange(2, phi)
    g = gcd(e, phi)
    while g != 1:
        e = random.randrange(2, phi)
        g = gcd(e, phi)

    d = modinv(e, phi)
    return ((e, n), (d, n))

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def modinv(a, m):
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

def encrypt(public_key, plaintext):
    e, n = public_key
    return [pow(ord(char), e, n) for char in plaintext]

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
        p, q = 61, 53
        public_key, private_key = generate_keypair(p, q)
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
        private_key = eval(request.form['private_key'])  # Harap hati-hati dengan eval

        if name in cards_data:
            encrypted_data = cards_data[name]['encrypted_data']
            d, n = private_key

            # Dekripsi data
            decrypted_card_number = ''.join([chr(pow(char, d, n)) for char in encrypted_data['card_number']])
            decrypted_expiry_date = ''.join([chr(pow(char, d, n)) for char in encrypted_data['expiry_date']])
            decrypted_cvv = ''.join([chr(pow(char, d, n)) for char in encrypted_data['cvv']])

            decrypted_message = {
                'card_number': decrypted_card_number,
                'expiry_date': decrypted_expiry_date,
                'cvv': decrypted_cvv
            }

    return render_template('decrypt_card.html', decrypted_message=decrypted_message)

if __name__ == "__main__":
    app.run(debug=True)
