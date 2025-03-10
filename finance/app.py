from flask import Flask, request, jsonify, render_template
import openai

app = Flask(__name__)

# Khởi tạo OpenAI API
openai.api_key = 'YOUR_OPENAI_API_KEY'

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('message')
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=user_input,
        max_tokens=150
    )
    return jsonify({'response': response.choices[0].text.strip()})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)