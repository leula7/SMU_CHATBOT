### Author: Riya Nakarmi ###
### College Project ###

import random
import json
import pickle
import numpy as np
import tensorflow
import nltk
from nltk.stem import WordNetLemmatizer

from keras.models import load_model

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


lemmatizer = WordNetLemmatizer()

intents = json.loads(open('intents.json').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbotmodel.h5')

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word)  for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words= clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1

    return np.array(bag)

insult = False
def sensetive_word(message, sensetive):
    # traverse in the 1st list
    for x in message:
        # traverse in the 2nd list
        for y in sensetive:
            # if one common
            if x == y:
                return True
    return insult

def forgiveness(message, forgive):
    # traverse in the 1st list
    for x in message:
        # traverse in the 2nd list
        for y in forgive:
            # if one common
            if x == y:
                return False
    return insult


def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda  x:x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list


def get_response(intents_list,intents_json):
    tag= intents_list[0]['intent']
    list_of_intents =intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result
def start_command(update,context):
    update.message.replay_text('Ask me anything you need to know about SMUC')

def help_command(update,context):
    update.message.replay_text('just ask anything')

updater = Updater('5800834136:AAEiJtxExevtOKqRseS8fyhkTR3DtiyrySk',use_context= True)
def handl_message(update,context):
    text = str(update.message.text)
    ints = predict_class(text)
    res = get_response(ints, intents)
    bot = updater.bot
    bot.send_message(chat_id=update.message.chat_id, text=res)
    update.message.replay_text(res)

def error(update,context):
    print(f"Update {update} casued error {context.error}")

def main():
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", start_command))
    dp.add_handler(MessageHandler(Filters.text, handl_message))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


main()


print("|============= Welcome to College Equiry Chatbot System! =============|")
print("|============================== Feel Free ============================|")
print("|================================== To ===============================|")
print("|=============== Ask your any query about our college ================|")
while True:
    message = input("| You: ")
    insult = sensetive_word(clean_up_sentence(message), intents['intents'][1]['patterns'])
    insult = forgiveness(clean_up_sentence(message), intents['intents'][2]['patterns'])
    if not insult:
        if message == "bye" or message == "Goodbye":
            ints = predict_class(message)
            res = get_response(ints, intents)
            print("| SMUC-Bot:", res)
            print("|===================== The Program End here! =====================|")
            exit()
        else:
            ints = predict_class(message)
            res = get_response(ints, intents)
            print("| SMUC-Bot:", res)
    else:
        ints = predict_class(message)
        res = get_response([{'intent': 'insults'}], intents)
        print("| SMUC-Bot:", res)