# shopassist_project
Submitted by Vishwjeet Singh Chauhan

1. Updated the flow to use Functional caliing
    a. "intent_confirmation_layer" now returns the desired dictionary object after checking whether all the keys can be inferred from user input
    b. "intent_confirmation_layer" executes one of the two defined functions conditionally
    c. If all the keys can be inferred it executes "extract_laptop_info_dict" function
    d. Other wise it executes "missing_keys" function
2. Reduced one call to LLM completely
    a. As "intent_confirmation_layer" now returns the disctionary, "dictionary_present" function is not being called
3. Added error handling at multiple places
    a. Handled the scenario when LLM returns a dictionary with less than 6 keys i.e. if any of the keys is missing
    b. And more
4. Created a new function "make_valid_dict" to validate the dictionary returned by LLM
5. Updated look and feel


How to run:
1. Create .env file in the root directory
2. Add OpenAI key as following
    openai_key=sk-demoacct-your_key_here
3. Navigate to the project root folder in anaconda prompt
4. Execute "python app.py"