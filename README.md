# FraudGuard AI Assistant

A professional-grade fraud analysis tool that combines natural language processing with intelligent data analysis to help detect and analyze fraudulent transactions.

## 🌟 Features

- **Natural Language Interface**: Ask questions about fraud analysis in plain English
- **Intelligent Analysis**: Powered by Mistral AI for advanced fraud detection
- **Interactive GUI**: Modern, user-friendly interface built with ttkbootstrap
- **Database Integration**: Direct connection to your SQL database
- **Export Capabilities**: Export analysis results to various formats
- **Email Integration**: Send analysis results directly via email

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- SQL Server database
- Internet connection (for AI features)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Mini-model-For-BI.git
cd Mini-model-For-BI
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download the required spaCy model:
```bash
python -m spacy download en_core_web_md
```

## 💻 Usage

1. Run the application:
```bash
python app_gui.py
```

2. Enter your database connection details:
   - Server name
   - Database name

3. Start asking questions! Here are some example queries:
   - "Show monthly fraud analysis summary"
   - "Get all transaction data"
   - "List categories with their total and fraudulent amounts"

## 🛠️ Project Structure

- `app_gui.py`: Main application file with GUI implementation
- `mistral_utils.py`: AI model integration
- `db_utils.py`: Database connection and query utilities
- `nlp_utils.py`: Natural language processing utilities
- `supported_questions.py`: Predefined question patterns

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Future Improvements

- Add support for more database types
- Implement real-time fraud detection
- Add more visualization options
- Enhance AI model capabilities
- Add user authentication
- Implement automated reporting

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Mistral AI for the AI model
- spaCy for NLP capabilities
- ttkbootstrap for the modern UI components

## 📧 Contact

### Project Maintainer
**Ron Solo**  
QA Automation Engineer at Cyber  
Email: Ronsolo929@gmail.com

For general questions or support, please open an issue in the repository.