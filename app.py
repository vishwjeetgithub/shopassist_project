from flask import Flask, redirect, url_for, render_template, request
from functions import initialize_conversation, initialize_conv_reco, get_chat_model_completions, moderation_check,intent_confirmation_layer,dictionary_present,compare_laptops_with_user,recommendation_validation

import openai
import ast
import re
import pandas as pd
import json
from os import environ
from dotenv import load_dotenv

load_dotenv()



# openai.api_key = open("api_key.txt", "r").read().strip()
openai.api_key = environ.get("openai_key")

app = Flask(__name__)

conversation_bot = []
conversation = initialize_conversation()
introduction = get_chat_model_completions(conversation)
conversation_bot.append({'bot':introduction})
conversation.append({"role": "assistant", "content": introduction})
top_3_laptops = None

# print("\n\nConversation initialization :: ", conversation, "\n")

@app.route("/")
def default_func():
    global conversation_bot, conversation, top_3_laptops
    return render_template("index_invite.html", name_xyz = conversation_bot)

@app.route("/end_conv", methods = ['POST','GET'])
def end_conv():
    global conversation_bot, conversation, top_3_laptops
    conversation_bot = []
    conversation = initialize_conversation()
    introduction = get_chat_model_completions(conversation)
    conversation_bot.append({'bot':introduction})
    top_3_laptops = None
    return redirect(url_for('default_func'))

@app.route("/invite", methods = ['POST'])
def invite():
    global conversation_bot, conversation, top_3_laptops, conversation_reco
    user_input = request.form["user_input_message"]
    # prompt = 'Remember your system message and that you are an intelligent laptop assistant. So, you only help with questions around laptop.'
    moderation = moderation_check(user_input)
    if moderation == 'Flagged':
        return redirect(url_for('end_conv'))

    print("\n\ntop_3_laptops :: ", top_3_laptops, "\n") # debug comment
    if (top_3_laptops is None) or (top_3_laptops.get("response_body")==[]):
        # conversation.append({"role": "user", "content": user_input + prompt})
        conversation.append({"role": "user", "content": user_input})
        conversation_bot.append({'user':user_input})

        print("\n\nConversation ::", conversation, "\n")

        response_assistant = get_chat_model_completions(conversation)
        # print("\n\nResponse assistant :: ", response_assistant, "\n") # Debug comment. Ask the model to return a json abject with all keys for all products
        
        moderation = moderation_check(response_assistant)
        if moderation == 'Flagged':
            return redirect(url_for('end_conv'))

        confirmation = intent_confirmation_layer(response_assistant) #This layer can be used to solve multiple purposes

        print("\n\nConfirmation :: ", confirmation, "\n") # Debug comment
        
        moderation = moderation_check(str(confirmation))
        if moderation == 'Flagged':
            return redirect(url_for('end_conv'))

        # if "No" in confirmation:
        if (confirmation.get("response_type") in ["missing_keys","None"]) or (len(confirmation.get("response_body"))<6):
            conversation.append({"role": "assistant", "content": response_assistant})
            conversation_bot.append({'bot':response_assistant})
        else:
            # response = dictionary_present(response_assistant) # This API call can be removed

            print("\n\nDictionary present :: ", confirmation, "\n") # Debug comment

            # moderation = moderation_check(confirmation)
            # if moderation == 'Flagged':
            #     return redirect(url_for('end_conv'))

            conversation_bot.append({'bot':"Thank you for providing all the information. Kindly wait, while I fetch the products: \n"})
            top_3_laptops = compare_laptops_with_user(confirmation.get("response_body"))
            if top_3_laptops.get("response_type")!="error":
                validated_reco = recommendation_validation(top_3_laptops.get("response_body"))

                if len(validated_reco) == 0:
                    conversation_bot.append({'bot':"Sorry, we do not have laptops that match your requirements. Connecting you to a human expert. Please end this conversation."})

                conversation_reco = initialize_conv_reco(validated_reco)
                recommendation = get_chat_model_completions(conversation_reco)

                moderation = moderation_check(recommendation)
                if moderation == 'Flagged':
                    return redirect(url_for('end_conv'))

                conversation_reco.append({"role": "user", "content": "This is my user profile" + str(confirmation.get("response_body"))})

                conversation_reco.append({"role": "assistant", "content": recommendation})
                conversation_bot.append({'bot':recommendation})

                print(f"\n\nRecommendations are :: {recommendation}\n")
            else:
                print("\n\nTried to process dictionary for final recomm, but compare laptop returned error\n")
                pass
    else:
        conversation_reco.append({"role": "user", "content": user_input})
        conversation_bot.append({'user':user_input})

        response_asst_reco = get_chat_model_completions(conversation_reco)

        moderation = moderation_check(response_asst_reco)
        if moderation == 'Flagged':
            return redirect(url_for('end_conv'))

        conversation.append({"role": "assistant", "content": response_asst_reco})
        conversation_bot.append({'bot':response_asst_reco})
    return redirect(url_for('default_func'))

if __name__ == '__main__':
    app.run(debug=True, host= "0.0.0.0")