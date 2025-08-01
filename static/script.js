document.addEventListener('DOMContentLoaded', function() {
    const scrapeBtn = document.getElementById('scrapeBtn');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.querySelector('.spinner');
    const results = document.getElementById('results');
    const error = document.getElementById('error');
    const summaryContent = document.getElementById('summaryContent');
    const errorMessage = document.getElementById('errorMessage');
    const contentLength = document.getElementById('contentLength');
    const timestamp = document.getElementById('timestamp');
    
    scrapeBtn.addEventListener('click', async function() {
        // Reset UI
        results.style.display = 'none';
        error.style.display = 'none';
        
        // Show loading state
        scrapeBtn.disabled = true;
        btnText.textContent = 'Generating Summary...';
        spinner.style.display = 'block';
        
        try {
            const response = await fetch('/api/scrape-and-summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Show results
                summaryContent.textContent = data.summary;
                contentLength.textContent = `Content processed: ${data.content_length} characters`;
                timestamp.textContent = `Generated: ${new Date().toLocaleString()}`;
                results.style.display = 'block';
            } else {
                // Show error
                errorMessage.textContent = data.error || 'An unexpected error occurred';
                error.style.display = 'block';
            }
            
        } catch (err) {
            console.error('Fetch error:', err);
            errorMessage.textContent = 'Network error: Unable to connect to the server';
            error.style.display = 'block';
        } finally {
            // Reset button state
            scrapeBtn.disabled = false;
            btnText.textContent = 'Generate Summary';
            spinner.style.display = 'none';
        }
    });
});