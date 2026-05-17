import os
import base64
import requests
import json

def analyze_image(image_path):
    """
    Analyzes an image using the Gemini REST API directly.
    This avoids all python package conflicts between MediaPipe and Google SDKs!
    Expects GEMINI_API_KEY environment variable to be set.
    """
    print(f"Vision AI analyzing image: {image_path}")
    
    if not os.path.exists(image_path):
        return "Error: Image file not found."
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("WARNING: GEMINI_API_KEY not set. Using fallback dummy response.")
        return "I see the selected area, but the Gemini API key is missing. Please set it to enable full Vision capabilities."
        
    try:
        # Read and encode the image
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        headers = {'Content-Type': 'application/json'}
        
        data = {
            "contents": [{
                "parts": [
                    {"text": "You are Touch AI's Vision module. The user has selected this area of their screen using a Google Lens style gesture. Analyze this image. If there is text, read it and summarize it or answer any implicit questions. If it's an image, describe it briefly and helpfully."},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": encoded_string
                        }
                    }
                ]
            }]
        }
        
        print("Sending request to Gemini Vision API...")
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            result = response.json()
            try:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print("Vision Analysis Result:", text)
                return text
            except (KeyError, IndexError):
                return "The Vision AI analyzed the image, but couldn't formulate a response."
        else:
            print(f"Vision API Error: {response.status_code} - {response.text}")
            return "An error occurred while contacting the Vision AI servers."
            
    except Exception as e:
        print(f"Error during Vision Analysis: {e}")
        return "An error occurred while analyzing the image."

if __name__ == "__main__":
    # Test
    # analyze_image("lens_capture.png")
    pass
