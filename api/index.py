from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def scrape_sanctions_page():
    """Scrape the UK Russia sanctions guidance page"""
    url = "https://www.gov.uk/government/publications/russia-sanctions-guidance/russia-sanctions-guidance"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract main content - UK gov sites typically use specific classes
        content_selectors = [
            '.govspeak',
            '.gem-c-govspeak',
            'main',
            '.publication-external-attachment',
            'article'
        ]
        
        content_text = ""
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                # Remove script and style elements
                for script in content_div(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                content_text = content_div.get_text(separator='\n', strip=True)
                break
        
        if not content_text:
            # Fallback: get all text from body
            body = soup.find('body')
            if body:
                for script in body(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                content_text = body.get_text(separator='\n', strip=True)
        
        # Clean up the text
        content_text = re.sub(r'\n+', '\n', content_text)
        content_text = re.sub(r'\s+', ' ', content_text)
        
        # Limit content length for API processing
        if len(content_text) > 8000:
            content_text = content_text[:8000] + "..."
        
        return content_text, url
        
    except Exception as e:
        return f"Error scraping website: {str(e)}", url

def generate_summary(content):
    """Generate summary using Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Please provide a comprehensive summary of the following UK Russia sanctions guidance content. 
        Focus on:
        1. Key sanctions measures
        2. Who they apply to
        3. Important compliance requirements
        4. Recent updates or changes
        5. Practical implications for businesses
        
        Content to summarize:
        {content}
        
        Please structure your response with clear headings and bullet points for easy reading.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error generating summary: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scrape-and-summarize', methods=['POST'])
def scrape_and_summarize():
    try:
        # Scrape the website
        content, url = scrape_sanctions_page()
        
        if content.startswith("Error"):
            return jsonify({
                'error': content,
                'url': url
            }), 500
        
        # Generate summary
        summary = generate_summary(content)
        
        return jsonify({
            'summary': summary,
            'url': url,
            'content_length': len(content)
        })
        
    except Exception as e:
        return jsonify({
            'error': f"Unexpected error: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True)