import PyPDF2
from nltk.tokenize import word_tokenize

# Open the PDF file
with open('file.pdf', 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    
    # Initialize a text variable to hold all the text
    text = ''
    
    # Iterate over each page in the PDF and extract text
    for page in reader.pages:
        text += page.extract_text()
        
# Tokenize the text
tokens = word_tokenize(text)

# Count the tokens
number_of_tokens = len(tokens)

print(f'The number of tokens in the PDF is: {number_of_tokens}')
