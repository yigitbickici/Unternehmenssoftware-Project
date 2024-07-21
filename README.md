# HireHelper Chatbot

**HireHelper Chatbot** is a sophisticated application designed to streamline recruitment processes by analyzing CVs and assisting with email communications. Developed using the LangChain framework, OpenAI's GPT-4, and Streamlit, this tool aims to enhance the efficiency of hiring decisions and candidate interactions.

## Features

- **CV Analysis:** Extracts and analyzes GitHub usernames and email addresses from PDF CVs.
- **Email Communication:** Allows sending customized emails to candidates.
- **Interactive Interface:** Provides a user-friendly interface for comparing and analyzing CVs based on selected features.
- **Powerful AI:** Utilizes GPT-4 for generating responses and processing text.

## Technologies Used

- **LangChain Framework**: For building and managing the chatbot infrastructure.
- **OpenAI GPT-4**: For natural language processing and response generation.
- **SMTP**: For email sending functionality.
- **Streamlit**: For creating an interactive and user-friendly frontend.
- **FAISS**: For efficient similarity search in vector space.

## Setup and Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yigitbickici/Unternehmenssoftware-Project.git
    cd Unternehmenssoftware-Project
    ```

2. **Install Dependencies:**

    Make sure you have Python 3.7 or higher installed. Then, install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up Environment Variables:**

    Create a `.env` file in the root directory of the project and add the following variables:

    ```env
    GITHUB_TOKEN=your_github_token
    ```

4. **Run the Application:**

    Launch the Streamlit app by running:

    ```bash
    streamlit run app.py
    ```

## Usage

1. **Upload PDF CVs:**

    Use the file uploader to upload multiple PDF CVs. The application will extract text, GitHub usernames, and email addresses from the PDFs.

2. **Compare and Analyze CVs:**

    Navigate to the "Comparing and Analyzing CV(s)" section. Select the features you want to compare and enter any custom prompts if needed. Click "Process" to analyze the CVs.

3. **Send Emails to Candidates:**

    Go to the "Send E-mail to Candidates" section. Select an email address, enter the subject, and describe the content you want to include in the email. Click "Send Email" to dispatch the email.

## Contributing

If you would like to contribute to the development of HireHelper Chatbot, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any questions or feedback, please reach out to [your-email@example.com](mailto:your-email@example.com).

