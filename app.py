from flask import Flask, render_template, request, redirect, jsonify
import csv
import os
from difflib import get_close_matches

app = Flask(__name__)

CSV_FILE = 'clients.csv'

@app.route('/', methods=['GET', 'POST'])
def invoice():
    if request.method == 'POST':
        reference_no = request.form['referenceNo']
        date = request.form['date']
        client_name = request.form['clientName']
        client_address = request.form['clientAddress']
        remarks = request.form['remarks']

        particulars = []
        amounts = []
        for i in range(10):
            part = request.form.get(f'particular{i}')
            if part == 'Other':
                part = request.form.get(f'other{i}', '')
            amt = request.form.get(f'amount{i}', '')
            if part and amt:
                particulars.append(part)
                amounts.append(float(amt))

        total = sum(amounts)

        # Write to CSV
        file_exists = os.path.isfile(CSV_FILE)
        with open(CSV_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Reference No", "Date", "Client Name", "Client Address", "Remarks", "Particulars", "Amounts", "Total"])
            writer.writerow([
                reference_no,
                date,
                client_name,
                client_address,
                remarks,
                '|'.join(particulars),
                '|'.join(map(str, amounts)),
                round(total, 2)
            ])

        return "Invoice Saved!"

    return render_template('form.html')


@app.route('/client-suggestions')
def client_suggestions():
    query = request.args.get('query', '').strip().lower()
    suggestions = []
    seen = set()

    if not query:
        return jsonify([])

    # Read client names and addresses from CSV
    with open('clients.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        records = []
        for row in reader:
            name = row['Client Name'].strip()
            address = row['Client Address'].strip()
            if name.lower().startswith(query) or query in name.lower():
                records.append({'name': name, 'address': address})
            elif query in name.lower():
                records.append({'name': name, 'address': address})

    # Remove duplicates and limit to 7
    for record in records:
        if record['name'] not in seen:
            suggestions.append(record)
            seen.add(record['name'])
            if len(suggestions) >= 7:
                break

    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True)
