# YouTube Video Summarizer

This Streamlit application allows users to summarize YouTube video transcripts using Google's Gemini-2.5-Flash model.

## Features:
- Summarizes YouTube videos by link.
- Offers different summary styles (e.g., Professional, Casual, Concise).
- Allows setting a custom word limit for summaries.
- Provides options to download summaries as .txt or .pdf files.

## How to Run Locally:

To run this application on your local machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/gokulkrishna1686/youtube-video-summarizer.git](https://github.com/gokulkrishna1686/youtube-video-summarizer.git)
    cd youtube-video-summarizer
    ```
    *(When you run the `git clone` command, it will create a new folder named `youtube-video-summarizer` on your computer, and the `cd` command then moves you into that folder.)*

2.  **Create and activate a virtual environment:**
    It's good practice to use a virtual environment to manage dependencies.
    * **On Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    * **On macOS / Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    Ensure you have all the required libraries installed.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Update your Gemini API Key directly in `app.py`:**
    * Open the `app.py` file in your project.
    * Find the line `genai.configure(api_key=st.secrets["GEMINI_API_KEY"])`
    * Change it to:
        ```python
        genai.configure(api_key="YOUR_GEMINI_API_KEY") # replace with your actual Gemini API key
        ```
        *(**Important Security Note:** For deployed applications or collaborative projects, it's best practice to keep API keys out of the code using environment variables or secret management services like Streamlit Secrets. This direct update is for simplified local testing.)*

5.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
    This will open the application in your web browser.

## Known Issues / Deployment Notes:

Please be aware of the following challenge, particularly concerning cloud deployment:

* **YouTube IP Blocking:** YouTube aggressively blocks automated requests for transcripts, especially from IP addresses belonging to cloud providers (like Streamlit Cloud). Due to this, the application may **fail to fetch transcripts when deployed on Streamlit Cloud** or similar environments. To ensure the website runs, it is recommended to run it **locally**. When running locally, you will need to update the `genai.configure` line in `app.py` with your personal Gemini API key. This direct connection from a local IP is often less prone to immediate blocking than cloud IPs.

---