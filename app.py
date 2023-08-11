
from flask import Flask, request, render_template
import openai
import re
from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import numpy as np
import configparser
app = Flask(__name__)
app.static_folder = 'static'

config = configparser.ConfigParser()
config.read('config.ini')

# Connect to MongoDB
client = MongoClient(
    # 'mongodb+srv://talhaidrees:T12345678@cluster0.ii1kmj4.mongodb.net/?retryWrites=true&w=majority'
    "mongodb+srv://talhaidrees:talhaidrees@cluster0.pyvhpsm.mongodb.net/TravelChatbot?retryWrites=true&w=majority"
    )
db = client['TravelChatbot']
hotels_collection = db['hotels']

# openai.api_key = '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'
openai_secret_key = config.get('openai_api_credentials', 'api_secret_key', fallback=None)
openai.api_key = openai_secret_key
# Memory DF
df = pd.read_csv("memory.csv")
df.drop(['Unnamed: 0'], axis=1, inplace=True)
# empty_row = pd.Series({}, name=len(df))
# df = df.append(empty_row)

df.loc[len(df)] = [np.nan for i in range(len(df.columns))]

# print(df, df.shape)

global_vars = {}  # Dictionary to store global variables


def chat_with_model(prompt):
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=1000,
        temperature=0.2,
        n=1,
        stop=None,
        echo=None
    )

    return {
        'response': response.choices[0].text.strip()
    }


def calculate_price(hotel, df):
    p = ""
    try:
        # if str(df['no_of_kids'].iloc[0]) != 'nan':
        if hotel['Tipo offerta'] == 'Costo giornaliero':
            if str(df['no_of_kids'].iloc[0]) != '0.0' and str(df['age_of_kids'].iloc[0] != 'nan'):
                print("First Price If")
                if str(hotel['Prezzo HB']) != 'nan' and str(hotel['Prezzo FB']) != 'nan':
                    p += f'''
                        In a hotel, there are {df['no_of_persons'].iloc[0]} adults and {df['no_of_kids'].iloc[0]} kids which are staying for {df['nights'].iloc[0]} nights. The price per night for Half Board (HB) is ${str(hotel['Prezzo HB'])}, and for Full Board (FB) is ${str(hotel['Prezzo FB'])}.
                        The age of the kids is: "{df['age_of_kids'].iloc[0]}". 
                        The "discount rules" for adults and kids both are described below in italian language:
                        "Infant da 0 a 2,99 gratuiti 3°/4° letto 3/11,99 anni sconto del 50% 3°/4° letto dai 12 anni ai 17,99 sconto del 25%  3°/4° letto da 18 anni sconto del 10%"
                        
                        By seeing the above rules, calculate the discount price for all the kids by seeing the ages of kids in "df['age_of_kids'].iloc[0]". Then store the final result in discount_kids_hb for HB and discount_kids_fb for FB.

                        Once the kids price calculation part is done, now its time to calculate adults price discount. If the discount for adults is given in "discount rules" then calculate price like below:
                        discount_adults_hb = no_of_persons * nights * hotel['Prezzo HB'] * adults discount percentage
                        discount_adults_fb = no_of_persons * nights * hotel['Prezzo FB'] * adults discount percentage

                        Otherwise, if discount for adults is not present in "discount rules" then calculate price like below:
                        discount_adults_hb = no_of_persons * nights * hotel['Prezzo HB']
                        discount_adults_fb = no_of_persons * nights * hotel['Prezzo FB']

                        Once the discount for kids and adults both are calculated, now its time to sum them and save the final results in two variables total_price_hb for HB and total_price_fb for FB.
                        Note: Don't use any indentation in the code and don't write any comments. So, let's write a python code for this
                        ''' 
                        
                elif str(hotel['Prezzo HB']) != 'nan':
                    p += f'''
                        {df['no_of_persons'].iloc[0]} persons and {df['no_of_kids'].iloc[0]} kids of age {df['age_of_kids'].iloc[0]} years are staying in a hotel for {df['nights'].iloc[0]} nights. Per night Price of the hotel is {str(hotel['Prezzo HB'])} for HB. Below is the discount for the age_of_kids: 

                        {hotel['Riduzioni offerta']}

                        Store the kids discount of HB in discount_price_hb = no_of_kids * (Prezzo_HB * discount percentage by seeing above rules for kids age) * no_of_nights.
                        
                        Store the result for HB in total_price_hb = (no_of_persons * Prezzo_HB * no_of_nights) + discount_price_hb

                        Write only a python code to give me the total price in variable total_price_hb for the HB.
                    
                    '''
                elif str(hotel['Prezzo FB']) != 'nan':
                    p += f'''
                        {df['no_of_persons'].iloc[0]} persons and {df['no_of_kids'].iloc[0]} kids of age {df['age_of_kids'].iloc[0]} years are staying in a hotel for {df['nights'].iloc[0]} nights. Per night Price of the hotel is {str(hotel['Prezzo FB'])} for FB. Below is the discount for the age_of_kids: 

                        {hotel['Riduzioni offerta']}

                        Store the kids discount of FB in discount_price_fb = no_of_kids * (Prezzo_FB * discount percentage by seeing above rules for kids age) * no_of_nights.
                        
                        Store the result for FB in total_price_fb = (no_of_persons * Prezzo_FB * no_of_nights) + discount_price_hb

                        Write only a python code to give me the total price in variable total_price_fb for the FB.
                    
                    '''
            elif str(df['no_of_kids'].iloc[0]) == str(0.0) or str(df['no_of_kids'].iloc[0]) == 'nan':
                print("Second Price If")

                if str(hotel['Prezzo HB']) != 'nan' and str(hotel['Prezzo FB']) != 'nan':
                    p += f'''
                        {df['no_of_persons'].iloc[0]} persons are staying in a hotel for {df['nights'].iloc[0]} nights. Per night Price of the hotel is {str(hotel['Prezzo HB'])} for HB and {str(hotel['Prezzo FB'])} for FB.

                        Write only a python code to give me the total price in variable total_price_hb for the HB and total_price_fb for the FB.
                    '''
                elif str(hotel['Prezzo HB']) != 'nan':
                    p += f'''
                        {df['no_of_persons'].iloc[0]} persons are staying in a hotel for {df['nights'].iloc[0]} nights. Per night Price of the hotel is {str(hotel['Prezzo HB'])} for HB.
                        
                        Write only a python code to give me the total price in variable total_price_hb.
                    '''
                elif str(hotel['Prezzo FB']) != 'nan':
                    p += f'''
                        {df['no_of_persons'].iloc[0]} persons are staying in a hotel for {df['nights'].iloc[0]} nights. Per night Price of the hotel is {str(hotel['Prezzo FB'])} for FB.

                        Write only a python code to give me the total price in variable total_price_fb.
                    '''
        elif hotel['Tipo offerta'] == 'Totale offerta' or str(hotel['Tipo offerta'] == 'Totale offerta') != 'nan':
            print("Totale offerta", True)
            if str(df['no_of_kids'].iloc[0]) != '0.0' and str(df['age_of_kids'].iloc[0] != 'nan'):
                print("First Price If")
                if str(hotel['Prezzo HB']) != 'nan' and str(hotel['Prezzo FB']) != 'nan':
                    p += f'''
                        There are {df['no_of_persons'].iloc[0]} persons and {df['no_of_kids'].iloc[0]} kids of age {df['age_of_kids'].iloc[0]} years. Per night Price of the hotel is {str(hotel['Prezzo HB'])} for HB and {str(hotel['Prezzo FB'])} for FB. Below is the discount for the age_of_kids: 

                        {hotel['Riduzioni offerta']}
                        Store the kids discount of HB in discount_price_hb = no_of_kids * (Prezzo_HB * discount percentage by seeing above rules for kids age).
                        Same do for FB discount_price_fb = no_of_kids * (Prezzo_FB * discount percentage by seeing above rules for kids age).
                        
                        Store the result for HB in total_price_hb = (no_of_persons * Prezzo_HB) + discount_price_hb
                        Store the result for FB in total_price_fb = (no_of_persons * Prezzo_FB) + discount_price_fb

                        Write only a python code to give me the total price in variable total_price_hb for the HB and total_price_fb for the FB.
                    '''
                elif str(hotel['Prezzo HB']) != 'nan':
                    p += f'''
                        There are {df['no_of_persons'].iloc[0]} persons and {df['no_of_kids'].iloc[0]} kids of age {df['age_of_kids'].iloc[0]} years. Per night Price of the hotel is {str(hotel['Prezzo HB'])} for HB. The discount for different ages of kids is described below: 

                        {hotel['Riduzioni offerta']}

                        Store the kids discount of HB in discount_price_hb = no_of_kids * (Prezzo_HB * discount percentage by seeing above rules for kids age)
                        
                        Store the result for HB in total_price_hb = (no_of_persons * Prezzo_HB) + discount_price_hb

                        Write only a python code to give me the total price in variable total_price_hb for the HB.
                    
                    '''
                elif str(hotel['Prezzo FB']) != 'nan':
                    p += f'''
                        There are {df['no_of_persons'].iloc[0]} persons and {df['no_of_kids'].iloc[0]} kids of age {df['age_of_kids'].iloc[0]} years. Per night Price of the hotel is {str(hotel['Prezzo FB'])} for FB. Below is the discount for the age_of_kids: 

                        {hotel['Riduzioni offerta']}
                        Store the kids discount of FB in discount_price_fb = no_of_kids * (Prezzo_FB * discount percentage by seeing above rules for kids age)
                        
                        Store the result for FB in total_price_fb = (no_of_persons * Prezzo_FB) + discount_price_hb

                        Write only a python code to give me the total price in variable total_price_fb for the FB.
                    '''
            elif str(df['no_of_kids'].iloc[0]) == str(0.0) or str(df['no_of_kids'].iloc[0]) == 'nan':
                print("Second Price If")

                if str(hotel['Prezzo HB']) != 'nan' and str(hotel['Prezzo FB']) != 'nan':
                    p += f'''
                        There are {df['no_of_persons'].iloc[0]} persons. Per night Price of the hotel is {str(hotel['Prezzo HB'])} for HB and {str(hotel['Prezzo FB'])} for FB.

                        Write only a python code to give me the total price in variable total_price_hb for the HB and total_price_fb for the FB.
                    '''
                elif str(hotel['Prezzo HB']) != 'nan':
                    p += f'''
                        There are {df['no_of_persons'].iloc[0]} persons. Per night Price of the hotel is {str(hotel['Prezzo HB'])} for HB.
                        
                        Write only a python code to give me the total price in variable total_price_hb.
                    '''
                elif str(hotel['Prezzo FB']) != 'nan':
                    p += f'''
                        There are {df['no_of_persons'].iloc[0]} persons. Per night Price of the hotel is {str(hotel['Prezzo FB'])} for FB.

                        Write only a python code to give me the total price in variable total_price_fb.
                    '''
        # p += "\nNote: If the value are in double, then assume it in integer always. \nStore the final calculated price in total_price_fb or total_price_hb"
        print("Price Prompt: ", p, "\n")
        res = chat_with_model(p)
        print("hotel['Tipo offerta']: ", hotel['Tipo offerta'])
        print("Price Response: ", res['response'])

        # res = "hotel_name = 'Collela'"
        # try:
        exec(res['response'], global_vars)
        # except Exception as e:
        #     response = res['response'].split('\n')[3:]
        #     response = '\n'.join(response)
        #     exec(response, global_vars)
        total_price = ""
        try:
            global_vars['total_price_hb'] = abs(global_vars['total_price_hb'])
            global_vars['total_price_fb'] = abs(global_vars['total_price_fb'])
            total_price_hb = global_vars['total_price_hb']
            total_price_fb = global_vars['total_price_fb']
            total_price += "\nTotal Price for Half Board: " + str(int(total_price_hb)) + "€" + "\nTotal Price for Full Board: " + str(int(total_price_fb)) + "€"
        except:
            try:
                total_price_hb = global_vars['total_price_hb']
                total_price += "\nTotal Price for Half Board: " + str(int(total_price_hb)) + "€"
            except:
                try:
                    total_price_fb = global_vars['total_price_fb']
                    total_price += "\nTotal Price for Full Board: " + str(int(total_price_fb)) + "€"
                except Exception as e:
                    print("Total Price Exception: ", e)
                    total_price += "\n Something went wrong while calculating price"
                    total_price += f"""\nI understood something wrong may be. This is what I understood from previous conversation. Please tell me if I missed anything:\n\n
                                Hotel: {df['hotel_name'].iloc[0]}\n
                                Offer: {df['offer'].iloc[0]}\n
                                Your plan to stay: {df['valid_dal'].iloc[0]} to {df['valid_al'].iloc[0]}\n
                                Persons: {df['no_of_persons'].iloc[0]}\n
                                Kids: {str(df['no_of_kids'].iloc[0])}\n
                                Nights: {df['nights'].iloc[0]}\n
                            """

        print("Total Price: ", total_price)
        df.iloc[0] = np.nan
        return total_price
    except Exception as e:
        print("Price Exception: ", e)
        return f"""\nI didn't understand it I think. This is what I understood from previous conversation. Please tell me if I missed anything:\n\n
            Hotel: {hotel['Nome Hotel']}\n
            Your plan to stay: {df['valid_dal'].iloc[0]} to {df['valid_al'].iloc[0]}\n
            Persons: {df['no_of_persons'].iloc[0]}\n
            Kids: {str(df['no_of_kids'].iloc[0])}\n
            Nights: {df['nights'].iloc[0]}\n
        """


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/reset")
def reset():
    df.iloc[0] = np.nan
    print("Reset DF: ", df)
    return "Done"


@app.route('/chat', methods=['POST', 'GET'])
def hotel_check():
    user_prompt = request.args.get('msg')
    print(user_prompt)
    prompt = """
    Only return me the python code in variables like below:
    1. If hotel name is present in prompt, then write hotel_name = "name of hotel"
    2. If start date is present in prompt, then write valid_dal = "start date".
    3. If end date is present in prompt, then write valid_al = "end date"
    4. If number of nights is present in prompt, then write nights = nights number
    5. If number of adult persons is present in prompt, then write no_of_persons = no. of adult persons
    6. If number of kids is present in prompt, then write no_of_kids = no. of kids
    7. If user tell me the age of kids in prompt then store the complete user prompt (sentence) in variable age_of_kids. So, age_of_kids = complete user prompt at the end
    8. If user tell me the offer in prompt e.g (I want to go with specific offer), then save that complete offer in variable offer=specific offer that you talked in prompt

    Note: hotel_name can't be equal to offer variable
    Note: If any one of field is not present in user prompt then store 'nan' in it. So, write like variable_name = 'nan'
    Always write the date in this format in string e.g. "13/05/2023". If the user only tell the day and month, then you should assume that its 2023 year.

    Note: Don't perform any indentation in code.
    Note: If in the prompt, there will be written text in a format "year_number years". Then this means this is basically the age of kid. So store the year_number only in age_of_kids variable and don't alter the start and end date please
    Generate python code for above variables of exact below prompt.  \n
    Process the below prompt exactly and get variable names. Do not edit the prompt by yourself.
    """
    prompt += user_prompt

    if str(df['hotel_name'].iloc[0]) != 'nan':
        prompt += "Previously, I have hotel name is " + str(df['hotel_name'].iloc[0])
    if str(df['valid_dal'].iloc[0]) != 'nan' and str(df['valid_al'].iloc[0]) != 'nan':
        prompt += "Previously, I told that we are staying from " + str(df['valid_dal'].iloc[0]) + " to " + str(df['valid_al'].iloc[0]) + ". And it should remain same until new arrives"

    prompt += ". But you update the variable according to first sentence in this whole line which is: '" + user_prompt + "'"
    res = chat_with_model(prompt)
    print(res['response'])

    # res = "hotel_name = 'Collela'"
    try:
        exec(res['response'], global_vars)
    except Exception as e:
        response = res['response'].split('\n')[3:]
        response = '\n'.join(response)
        exec(response, global_vars)

    hotel_name = global_vars['hotel_name']
    valid_dal = global_vars['valid_dal']
    valid_al = global_vars['valid_al']
    nights = global_vars['nights']
    no_of_persons = global_vars['no_of_persons']
    no_of_kids = global_vars['no_of_kids']
    age_of_kids = global_vars['age_of_kids']
    offer = global_vars['offer']

    # print("global_vars", global_vars)
    # return ''
    try:
        if (hotel_name != 'nan'):
            df['hotel_name'].iloc[0] = hotel_name
        if (valid_dal != 'nan'):
            df['valid_dal'].iloc[0] = valid_dal
        if (valid_al != 'nan'):
            df['valid_al'].iloc[0] = valid_al
        if (nights != 'nan'):
            df['nights'].iloc[0] = int(nights)
        if (offer != 'nan'):
            df['offer'].iloc[0] = str(offer)
        if (no_of_persons != 'nan'):
            df['no_of_persons'].iloc[0] = int(no_of_persons)
        if (no_of_kids != 'nan'):
            df['no_of_kids'].iloc[0] = int(no_of_kids)
        if (age_of_kids != 'nan'):
            df['age_of_kids'].iloc[0] = age_of_kids
    except Exception as e:
        return "I didn't understand. Please ask something else"

    response = """"""

    if str(valid_dal) != 'nan' and str(valid_al) != 'nan':
        start_date = datetime.strptime(valid_dal, '%d/%m/%Y')
        end_date = datetime.strptime(valid_al, '%d/%m/%Y')

        diff = start_date - end_date
        n = abs(diff.days)
        print("Nights: ", n)
        df['nights'].iloc[0] = int(n)

    # print("Data Frame: ", df)

    # if str(df['hotel_name'].iloc[0]) != 'nan' and str(df['valid_dal'].iloc[0]) != 'nan' and str(df['valid_al'].iloc[0]) != 'nan' and str(df['nights'].iloc[0]) != 'nan' and str(df['no_of_persons'].iloc[0]) != 'nan' and str(df['no_of_kids'].iloc[0]) == 0:
    #     price = calculate_price()
    #     response

    # If the user chosen the offer then get the offer from DB
    if str(df['offer'].iloc[0]) != 'nan' and str(offer) != 'nan':
        print("First If\n")
        offer_str = df['offer'].iloc[0]
        query = {'Nome Offerta': offer_str,
                 'Attiva / Non attiva': True
                 }
        result = hotels_collection.find(query).limit(1)
        if result is not None:
            response += "\nOkay, you choosed below offer:"
            c = 0
            for hotel in result:
                df['hotel_name'].iloc[0] = hotel['Nome Hotel'] # Save Hotel Name
                response += f"\n\nOffer: {hotel['Nome Offerta']}\nHotel: {hotel['Nome Hotel']} \nAvailablity: {str(hotel['Valida dal'].strftime('%d-%m-%Y'))} to {str(hotel['Valida al'].strftime('%d-%m-%Y'))} \n"
                # Check nights and ask next questions
                if str(df['nights'].iloc[0]) != 'nan':
                    if int(df['nights'].iloc[0]) >= int(hotel['Minimo notti']) and int(df['nights'].iloc[0]) <= int(hotel['Massimo notti']):
                        # If user start date is less than DB start date
                        if start_date < hotel['Valida dal']:
                            response += "\nYour start date should be " + hotel['Valida dal'].strftime("%d-%m-%Y")
                            c += 1
                        elif end_date > hotel['Valida al']:
                            response += "\nYour end date should be " + hotel['Valida al'].strftime("%d-%m-%Y")
                            c += 1
                        else:
                            if str(df['no_of_persons'].iloc[0]) == 'nan' and str(df['no_of_kids'].iloc[0]) == 'nan' and c == 0:
                                response += "\nHow many persons and your kids are planning to stay? e.g (5 persons and 0 kids) \n"
                                c += 1
                            elif str(df['no_of_persons'].iloc[0]) == 'nan':
                                response += "\nHow many persons are planning to stay? e.g (5 persons or 0 persons) \n"
                                c += 1
                            elif str(df['no_of_kids'].iloc[0]) == 'nan':
                                response += "\nHow many of your kids are planning to stay? e.g (5 kids or 0 kids) \n"
                                c += 1
                            elif ((str(df['no_of_kids'].iloc[0]) != '0.0') and str(df['age_of_kids'].iloc[0]) == 'nan') and c == 0:
                                response += "\nWhat is the age of kids? e.g (Age of kids is 4-10 years) \n"
                                c += 1

                        # If everything is correct then calculate price
                        if c == 0:
                            price = calculate_price(hotel, df)
                            response += str(price)
                    else:
                        response += "\nIt looks like you want to stay for " + str(int(df['nights'].iloc[0])) + " nights. You can only stay for minimum " + str(hotel['Minimo notti']) + " and maximum " + str(
                            hotel['Massimo notti']) + " nights" + "\n" + "Write the appropriate date range by seeing minimum and maximum number of nights? e.g(5 june 2023 to 10 june 2023)"

        else:
            response += f'No hotel found matching your offer "{offer_str}" \nAsk me something else please'

#     elif str(df['hotel_name'].iloc[0]) != 'nan' and hotel_name != 'nan':
#         print("Second If\n")
#         hotel_name = df['hotel_name'].iloc[0]
#         start_date_str = df['valid_dal'].iloc[0]
#         end_date_str = df['valid_al'].iloc[0]

#         # Hotel name find pattern
#         search_words = hotel_name.split()
#         regex_patterns = [re.compile(re.escape(word), re.IGNORECASE)
#                           for word in search_words]

#         if str(df['valid_dal'].iloc[0]) == 'nan':
#             query = {}
#             if str(df['offer'].iloc[0]) != 'nan':
#                 # query = {'Nome Hotel': {'$in': regex_patterns},
#                 query = {'Nome Hotel': hotel_name,
#                         'Attiva / Non attiva': True,
#                         'Nome Offerta': str(df['offer'].iloc[0])
#                         }
#             else:
#                 # query = {'Nome Hotel': {'$in': regex_patterns},
#                 query = {'Nome Hotel': hotel_name,
#                         'Attiva / Non attiva': True,
#                         }
#             result = hotels_collection.find(query).limit(1)

#             # if result:
#             hotel_nome = []
#             hotel_pacchetto = []
#             for hotel in result:
#                 s1 = hotel['Nome Hotel']
#                 s2 = hotel['Pacchetto']
#                 hotel_nome.append(s1)
#                 hotel_pacchetto.append(s2)

# #             response += "Here are the top " + str(len(hotel_nome)) + " hotels with benefits: \n\n"
#             if hotel_nome:
#                 response += "Here is this hotel with detailed info: \n\n"
#                 for i in range(len(hotel_nome)):
#                     # response += str(hotel_nome[i]) + ": " + str(hotel_pacchetto[i]) + "\n"
#                     response += "Hotel: " + str(hotel['Nome Hotel']) + "\n" + "Available: " + str(hotel['Valida dal'].strftime(
#                         "%d-%m-%Y")) + " to " + str(hotel['Valida al'].strftime("%d-%m-%Y")) + "\n" + "Benefits: " + str(hotel["Pacchetto"]) + "\n"

#                 response += "\nTell us that from which start and end date you want to stay in " + hotel_name + "?"
#             # else:
#             #     response += "No hotel found for " + str(hotel_name)
#             if len(response) < 1:
#                 # if str(hotel_name_str) != 'nan':
#                 response += "No hotel found for " + str(hotel_name)
#                 df.iloc[0] = np.nan
#                 # response += str(hotel_name) + " is not available between " + str(start_date_str) + " and " + str(end_date_str)

#         elif str(start_date_str) != 'nan' and str(end_date_str) != 'nan':
#             start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
#             end_date = datetime.strptime(end_date_str, '%d/%m/%Y')
#             query = {}
#             if str(df['offer'].iloc[0]) != 'nan':
#                 query = {
#                     '$and': [
#                         # {'Nome Hotel': {'$in': regex_patterns}},
#                         {'Nome Hotel': hotel_name},
#                         {'Valida dal': {'$lte': end_date}},
#                         {'Valida al': {'$gte': start_date}},
#                         {'Attiva / Non attiva': True},
#                         {'Nome Offerta': str(df['offer'].iloc[0])}
#                     ]
#                 }
#             else:
#                 query = {
#                     '$and': [
#                         # {'Nome Hotel': {'$in': regex_patterns}},
#                         {'Nome Hotel': hotel_name},
#                         {'Valida dal': {'$lte': end_date}},
#                         {'Valida al': {'$gte': start_date}},
#                         {'Attiva / Non attiva': True}
#                     ]
#                 }
#             result = hotels_collection.find(query).limit(1)

#             c = 0
#             for hotel in result:
#                 response += "Hotel: " + str(hotel['Nome Hotel']) + "\n" + "Available: " + str(hotel['Valida dal'].strftime(
#                     "%d-%m-%Y")) + " to " + str(hotel['Valida al'].strftime("%d-%m-%Y")) + "\n" 
#                 # + "Benefits: " + str(hotel["Pacchetto"]) + "\n"
                
#                 # Check nights and ask next questions
#                 if str(df['nights'].iloc[0]) != 'nan':
#                     if int(df['nights'].iloc[0]) >= int(hotel['Minimo notti']) and int(df['nights'].iloc[0]) <= int(hotel['Massimo notti']):
#                         # If user start date is less than DB start date
#                         if start_date < hotel['Valida dal']:
#                             response += "\nYour start date should be " + hotel['Valida dal'].strftime("%d-%m-%Y")
#                             c += 1
#                         elif end_date > hotel['Valida al']:
#                             response += "\nYour end date should be " + hotel['Valida al'].strftime("%d-%m-%Y")
#                             c += 1
#                         else:
#                             if str(df['no_of_persons'].iloc[0]) == 'nan' and str(df['no_of_kids'].iloc[0]) == 'nan' and c == 0:
#                                 response += "\nHow many persons and your kids are planning to stay? e.g (5 persons and 0 kids) \n"
#                                 c += 1
#                             elif str(df['no_of_persons'].iloc[0]) == 'nan':
#                                 response += "\nHow many persons are planning to stay? e.g (5 persons) \n"
#                                 c += 1
#                             elif str(df['no_of_kids'].iloc[0]) == 'nan':
#                                 response += "\nHow many of your kids are planning to stay? e.g (5 kids) \n"
#                                 c += 1
#                             elif ((str(df['no_of_kids'].iloc[0]) != '0.0') and str(df['age_of_kids'].iloc[0]) == 'nan') and c == 0:
#                                 response += "\nWhat is the age of kids? e.g (Age of kids is 4-10 years) \n"
#                                 c += 1

#                         # If everything is correct then calculate price
#                         if c == 0:
#                             price = calculate_price(hotel, df)
#                             response += str(price)
#                     else:
#                         response += "\nIt looks like you want to stay for " + str(int(df['nights'].iloc[0])) + " nights. You can only stay for minimum " + str(hotel['Minimo notti']) + " and maximum " + str(
#                             hotel['Massimo notti']) + " nights" + "\n" + "Write the appropriate date range by seeing minimum and maximum number of nights? e.g(5 june 2023 to 10 june 2023)"

#             print("C: ", c)
#             if len(response) < 1:
#                 # if str(hotel_name_str) != 'nan':
#                 response += str(hotel_name) + " is not available between " + str(start_date_str) + " and " + str(end_date_str)
#         else:
#             response += "\nTell us that from which start and end date you want to stay in " + hotel_name + "?"

    # Third If
    elif str(df['valid_dal'].iloc[0]) != 'nan' and str(df['valid_al'].iloc[0]) != 'nan':
        print("Third If \n")
        hotel_name_str = df['hotel_name'].iloc[0]
        start_date_str = df['valid_dal'].iloc[0]
        end_date_str = df['valid_al'].iloc[0]

        start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
        end_date = datetime.strptime(end_date_str, '%d/%m/%Y')

        query = {}
        if str(hotel_name_str) != 'nan':
            # Hotel name find pattern
            search_words = hotel_name_str.split()
            regex_patterns = [re.compile(
                re.escape(word), re.IGNORECASE) for word in search_words]

            if str(df['offer'].iloc[0]) != 'nan':
                query = {
                    '$and': [
                        # {'Nome Hotel': {'$in': regex_patterns}},
                        {'Nome Hotel': hotel_name_str},
                        {'Valida dal': {'$lte': end_date}},
                        {'Valida al': {'$gte': start_date}},
                        {'Attiva / Non attiva': True},
                        {'Nome Offerta': str(df['offer'].iloc[0])}
                    ]
                }
            else:
                query = {
                    '$and': [
                        # {'Nome Hotel': {'$in': regex_patterns}},
                        {'Nome Hotel': hotel_name_str},
                        {'Valida dal': {'$lte': end_date}},
                        {'Valida al': {'$gte': start_date}},
                        {'Attiva / Non attiva': True},
                    ]
                }
        else:
            if str(df['offer'].iloc[0]) != 'nan':
                query = {
                    '$and': [
                        {'Valida dal': {'$lte': end_date}},
                        {'Valida al': {'$gte': start_date}},
                        {'Attiva / Non attiva': True},
                        {'Nome Offerta': str(df['offer'].iloc[0])}
                    ]
                }
            else:
                query = {
                    '$and': [
                        {'Valida dal': {'$lte': end_date}},
                        {'Valida al': {'$gte': start_date}},
                        {'Attiva / Non attiva': True},
                    ]
                }
        
        # First time when it run then fetch 3 items otherwise 1 (because its chosen by user)
        result = {}
        if str(df['hotel_name'].iloc[0]) == 'nan':
            result = hotels_collection.find(query).limit(3)
        else:
            result = hotels_collection.find(query).limit(1)

        c = 0
        c2 = 0
        if result is not None:
            response += f"\nOk, there are some offers chosen for you:"
            for hotel in result:
                # if c2 == 0:
                # c2 += 1
                # df['hotel_name'].iloc[0] = str(hotel['Nome Hotel'])
                response += "\n\nOffer: " + str(hotel['Nome Offerta']) + "\nAvailable: " + str(hotel['Valida dal'].strftime("%d-%m-%Y")) + " to " + str(
                    hotel['Valida al'].strftime("%d-%m-%Y")) + "\n\nHotel: " + str(hotel['Nome Hotel'])
                if str(df['hotel_name'].iloc[0]) == 'nan':
                    response +=  "\n" + str(hotel["Hotel"]) + "\n"

                # Check nights and ask next questions
                if str(df['nights'].iloc[0]) != 'nan' and str(df['hotel_name'].iloc[0]) != 'nan':
                    if int(df['nights'].iloc[0]) >= int(hotel['Minimo notti']) and int(df['nights'].iloc[0]) <= int(hotel['Massimo notti']):

                        # If user start date is less than DB start date
                        if start_date < hotel['Valida dal']:
                            response += "\nYour start date should be " + hotel['Valida dal'].strftime("%d-%m-%Y")
                            c += 1
                        elif end_date > hotel['Valida al']:
                            response += "\nYour end date should be " + hotel['Valida al'].strftime("%d-%m-%Y")
                            c += 1
                        else:
                            # if str(df['no_of_persons'].iloc[0]) == 'nan' and c == 0:
                            #     response += "\nHow many persons are planning to stay? e.g (5 persons) \n"
                            #     c += 1
                            # if str(df['no_of_kids'].iloc[0]) == 'nan' and c == 0:
                            #     response += "\nDo you have any kids coming along with you? e.g (5 kids or 0 kids) \n"
                            #     c += 1
                            if str(df['no_of_persons'].iloc[0]) == 'nan' and str(df['no_of_kids'].iloc[0]) == 'nan' and c == 0:
                                response += "\nHow many persons and your kids are planning to stay? e.g (5 persons and 0 kids) \n"
                                c += 1
                            elif str(df['no_of_persons'].iloc[0]) == 'nan':
                                response += "\nHow many persons are planning to stay? e.g (5 persons) \n"
                                c += 1
                            elif str(df['no_of_kids'].iloc[0]) == 'nan':
                                response += "\nHow many of your kids are planning to stay? e.g (5 kids) \n"
                                c += 1
                            elif ((str(df['no_of_kids'].iloc[0]) != '0.0') and str(df['age_of_kids'].iloc[0]) == 'nan') and c == 0:
                                response += "\nWhat is the age of kids? e.g (Age of kids is 4-10 years) \n"
                                c += 1

                        # If everything is correct then calculate price
                        if c == 0:
                            price = calculate_price(hotel, df)
                            response += str(price)
                    else:
                        response += "\nIt looks like you want to stay for " + str(int(df['nights'].iloc[0])) + " nights. \n\nYou can only stay for minimum " + str(hotel['Minimo notti']) + " and maximum " + str(
                            hotel['Massimo notti']) + " nights" + "\n" + "Write the appropriate date range by seeing minimum and maximum number of nights? e.g (5 june 2023 to 10 june 2023)"

            # If hotel name is choosed by user but only the date
            if (str(df['hotel_name'].iloc[0]) == 'nan' and str(df['valid_dal'].iloc[0]) != 'nan' and str(df['valid_al'].iloc[0]) != 'nan'):
                # response += f"\n\nTell us the hotel name which you like the most?"
                response += f"\n\nWhich offer you like the most?"

        # if len(response) < 1 :
        else:
            if str(hotel_name_str) != 'nan':
                response += str(hotel_name_str) + " is not available between " + str(start_date_str) + " and " + str(end_date_str)
                # + "\n\nIt is available from " + str(hotel['Valida dal'].strftime("%d-%m-%Y")) + " to " + str(hotel['Valida al'].strftime("%d-%m-%Y"))

            else:
                response += "There is not any any hotel available between " + str(start_date_str) + " and " + str(end_date_str) + "\nChange your start and end date"

    if len(response) < 1:
        response += "\nPlease tell us in which hotel or from which start & end date you want to stay?"
    print("DF:\n", df)
    response_html = response.replace('\n', '<br>')

    return response_html


if __name__ == '__main__':
    # app.run()
    host = 'ec2-3-95-218-42.compute-1.amazonaws.com'
    port = 4000
    app.run(host=host, port=port)
    # app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000, debug=True)
    # app.run(port=8000, debug=True)



"""
You are connected to our travel agency chatbot. We have a database named TravelDB in MongoDB, which contains a collection named hotels. The hotels collection has the following fields:
1. Nome: The name of the hotel.
2. Valida dal: The start date when the hotel is available.
3. Valida al: The end date until which the hotel is available.
4. minimo notti: The minimum number of nights stay at the hotel.
5. massimo notti: The maximum number of nights stay at the hotel.
6. Pacchetto: Room packages offered by the hotel, such as air conditioning, internet-WiFi, dinner with three different menu options, pool, and TV with sky channels.
7. Prezzo HB: The room price per night for Half Board.
8. Prezzo FB: The room price per night for Full Board.
9. Riduzioni offerta: Discounts offered for children of different ages.

The fields "Nome", "Valida dal", "Valida al", "Pacchetto", and "Riduzioni offerta" are of string data type. The fields "minimo notti" and "massimo notti" are of integer data type. The fields "Prezzo HB" and "Prezzo FB" are of double data type.

We also have a file named memory.csv, which will be used to calculate the price of the hotel. The memory.csv has following columns in it:
1. Nome: The name of the hotel.
2. Valida dal: The start date when the hotel is available.
3. Valida al: The end date until which the hotel is available.
4. minimo notti: The minimum number of nights stay at the hotel.
5. massimo notti: The maximum number of nights stay at the hotel.
6. Riduzioni offerta: Discounts offered for children of different ages.
7. No. of adult persons: Total number of people living in hotel excluding kids
8. No. of kids: Total number of kids living in hotel with the adults
9. Age of kids: Age of the kids. This will help you to check in Riduzioni offerta for calculating price


Your ultimate goal is to provide the price of the hotel both "Prezzo HB" & "Prezzo FB". You should keep updating the memory.csv file based on the conversation. Let me explain how it works.

For example, if a user says, "I want to stay at Lacco Ameno hotel," you need to check if this hotel is present in our database. If it is, write the hotel name under the "Nome" column in memory.csv. Your response should be "Yes, this hotel is available. From which date do you want to stay?" If the hotel is not present, your response should be "No, this hotel is not available."

If the hotel is available, you should ask the user the next question within your response, which is "From which date do you want to stay?" This is because the next column after "Nome" in memory.csv is "Valida dal."

To summarize, you should answer the user by checking the database and keep asking the next question based on the next column in memory.csv until the "Age of kids" column is filled. Once you have all the required fields filled in memory.csv, calculate the price of the hotel using the values in memory.csv. If memory.csv is not completely filled, continue asking questions to the user.

Note:
1. "Lacco Ameno" hotel is just an example. The user can ask different questions like "I want to stay at a hotel from 7 June. Are there any hotels available?" In this case, you should show the user the top three available hotel names from that date and update the "Valida dal" field in the memory.csv file if any matching hotel is found in the database.
2. The discounts for children are provided in the "Riduzioni offerta" column in the database.

Scenerios:
Let me tell you some more scenerios to explain you better.
1. In the user prompt, if the user will say "I want to live in "
Now, please generate the Python code for the following user prompt:
"I want to live in Colella hotel from 7 june. Is it available ?"

"""
