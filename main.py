def ask_claude_direct(pdf_data, question):
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-sonnet-4-20250514",
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
        timeout=httpx.Timeout(
            300.0,      # Gesamt-Timeout auf 5 Minuten
            connect=30.0, 
            read=300.0,   # Read-Timeout auf 5 Minuten
            write=30.0, 
            pool=30.0
        )
    )
    logging.info(f"Claude API responded with status {response.status_code}")
    if response.status_code != 200:
        raise ValueError(f"Claude API error: {response.text}")
    return response.json()["content"]
