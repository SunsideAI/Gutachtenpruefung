from flask import Flask, request, jsonify
import base64
import httpx
import os
import logging



app = Flask(__name__)
logging.basicConfig(level=logging.INFO)



ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"



def fetch_and_encode_pdf(pdf_url):
    logging.info(f"Fetching PDF from URL: {pdf_url}")
    response = httpx.get(pdf_url, headers={"User-Agent": "Mozilla/5.0"}, follow_redirects=True)



    if response.status_code != 200:
        raise ValueError("Failed to fetch PDF file")



    if "pdf" not in response.headers.get("Content-Type", ""):
        raise ValueError(f"URL did not return a PDF (Content-Type was: {response.headers.get('Content-Type')})")



    if not response.content.startswith(b"%PDF"):
        raise ValueError("Fetched file is not a valid PDF")



    return base64.b64encode(response.content).decode("utf-8")



def ask_claude_direct(pdf_data, question):
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }



    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data
                        }
                    },
                    {
                        "type": "text",
                        "text": question
                    }
                ]
            }
        ]
    }





    logging.info("Sending request to Claude API...")
    response = httpx.post(
        CLAUDE_API_URL,
        json=payload,
        headers=headers,
        timeout=httpx.Timeout(60.0, connect=30.0, read=60.0, write=30.0, pool=30.0)
    )
    logging.info(f"Claude API responded with status {response.status_code}")



    if response.status_code != 200:
        raise ValueError(f"Claude API error: {response.text}")



    return response.json()["content"]



@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    if not data or 'pdf_url' not in data or 'question' not in data:
        return jsonify({"error": "pdf_url and question are required"}), 400



    try:
        pdf_data = fetch_and_encode_pdf(data["pdf_url"])
        result = ask_claude_direct(pdf_data, data["question"])
        return jsonify({"answer": result})
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)

