import streamlit as st
import plotly.graph_objects as go
import numpy as np
import numpy_financial as npf
import pandas as pd
from datetime import date

from plotly.subplots import make_subplots
from sender import Attachment, Mail, Message
from PIL import Image
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore

import requests



cred = credentials.Certificate('/Users/josephrambow/PycharmProjects/aim_builder/firebase_config.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://rn-testing-ae88d-default-rtdb.firebaseio.com/'
})
ref = db.reference('prospect')


# st.set_page_config(
#     page_title="Mortgage Calculator")

#email information
# fromaddr = "joseph.rambow@gmail.com"
# password = "rxkjzfwxopvubzii"
# smtpserver = "smtp.gmail.com"
# ssl = True
# smtpport = 465

# with open('/Users/josephrambow/PycharmProjects/aim_builder/mortg_styles.css')as f:
#  st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)


# Logo/Header
# image = Image.open('/Users/josephrambow/PycharmProjects/Project-BB/AIm wealth realty logo copy.png')
#
# with st.container():
#     st.image(image)


st.title("Mortgage Calculator")

# st.header("**Mortgage Balance**")


st.subheader("Purchase Details")


colPrice, colValue = st.columns(2)

with colPrice:
    purchaseprice = st.number_input("Enter your purchase price($): ", min_value=1000, step=1000, format='%i')

with colValue:
    homevalue = st.number_input("Enter the home's value($): ", min_value=1000, step=1000, format='%i')


dpayment = st.number_input("Enter your down payment($): ", min_value=1000, step=1000, format='%i')
mortgage = purchaseprice - dpayment

colMortBal, colIntRate = st.columns(2)

# with colMortBal:
#     mortgage = st.number_input("Enter your mortgage balance($): ", min_value=1000, step=1000, format='%i')
with colMortBal:
    st.caption('Estimated mortgage balance', unsafe_allow_html=False)
    st.text(mortgage)
with colIntRate:
    interest = st.number_input("Enter your interest rate(%): ", min_value=0.01, format='%f')

periodic_interest_rate = (1+interest)**(1/12) - 1

colYears, colPmtYr = st.columns(2)

with colYears:
    years = st.number_input("Enter your mortgage term: ", min_value=1, format='%i')
with colPmtYr:
    payments_year = st.number_input("Enter your payments per year: ", min_value=1, format='%i')

# colStartDte = st.columns(1)
#
# with colStartDte:
start_date = st.date_input("When do payments start?: ")

monthly_installment = -1*npf.pmt(periodic_interest_rate , payments_year, mortgage)


# Form
colFName, colLName, colEmail, colPhone = st.columns(4)
with colFName:
    fname = st.text_input("First Name")
with colLName:
    lname = st.text_input("Last Name")
with colEmail:
    email = st.text_input("Email Address")
with colPhone:
    phone = st.text_input("Phone Number")

FullName = fname + ' ' + lname

# Monthly Payment
# def payment():
#     pmt = -1 * npf.pmt(interest/12, years*payments_year, mortgage)
#     print(pmt)
#
# # Interest Payment
# ipmt = -1 * npf.ipmt(interest/payments_year, 1, years * payments_year, mortgage)
#
# # Principal Payment
# ppmt = -1 * npf.ppmt(interest/payments_year, 1, years * payments_year, mortgage)


# print(pmt, ipmt, ppmt)

# rng = pd.date_range(start_date, periods=years * payments_year, freq='MS')
# rng.name = "Payment Date"
# df = pd.DataFrame(index=rng, columns=['Payment', 'Principal Paid', 'Interest Paid', 'Ending Balance'], dtype='float')
# df.reset_index(inplace=True)
# df.index += 1
# df.index.name = "Period"
# df["Payment"] = -1 * npf.pmt(interest/12, years * payments_year, mortgage)
# df["Principal Paid"] = -1 * npf.ppmt(interest/payments_year, df.index, years * payments_year, mortgage)
# df["Interest Paid"] = -1 * npf.ipmt(interest/payments_year, df.index, years * payments_year, mortgage)
# df["Ending Balance"] = 0
# df.loc[1, "Ending Balance"] = mortgage - df.loc[1, "Principal Paid"]
# df = df.round(2)



# for period in range(2, len(df)+1):
#     previous_balance = df.loc[period-1, "Ending Balance"]
#     principal_paid = df.loc[period, "Principal Paid"]
#
#     if previous_balance == 0:
#         df.loc[period, ['Payment', 'Principal Paid', 'Interest Paid', 'Ending Balance']] == 0
#         continue
#     elif principal_paid <= previous_balance:
#         df.loc[period, 'Ending Balance'] = previous_balance - principal_paid

principal_remaining = np.zeros(payments_year)
interest_pay_arr = np.zeros(payments_year)
principal_pay_arr = np.zeros(payments_year)

for i in range(0, payments_year):

    if i == 0:
        previous_principal_remaining = mortgage
    else:
        previous_principal_remaining = principal_remaining[i - 1]

    interest_payment = round(previous_principal_remaining * periodic_interest_rate, 2)
    principal_payment = round(monthly_installment - interest_payment, 2)

    if previous_principal_remaining - principal_payment < 0:
        principal_payment = previous_principal_remaining

    interest_pay_arr[i] = interest_payment
    principal_pay_arr[i] = principal_payment
    principal_remaining[i] = previous_principal_remaining - principal_payment

month_num = np.arange(payments_year)
month_num = month_num + 1

principal_remaining = np.around(principal_remaining, decimals=2)

fig = make_subplots(
    rows=2, cols=1,
    vertical_spacing=0.03,
    specs=[[{"type": "table"}],
           [{"type": "scatter"}]
          ]
)

fig.add_trace(
        go.Table(
            header=dict(
                    values=['Month', 'Principal Payment($)', 'Interest Payment($)', 'Remaining Principal($)']
                ),
            cells = dict(
                    values =[month_num, principal_pay_arr, interest_pay_arr, principal_remaining]
                )
            ),
        row=1, col=1
    )

fig.add_trace(
        go.Scatter(
                x=month_num,
                y=principal_pay_arr,
                name= "Principal Payment"
            ),
        row=2, col=1
    )

fig.append_trace(
        go.Scatter(
            x=month_num,
            y=interest_pay_arr,
            name="Interest Payment"
        ),
        row=2, col=1
    )

fig.update_layout(title='Mortgage Installment Payment Over Months',
                   xaxis_title='Month',
                   yaxis_title='Amount($)',
                   height= 800,
                   width = 1200,
                   legend= dict(
                           orientation="h",
                           yanchor='top',
                           y=0.47,
                           xanchor= 'left',
                           x= 0.01
                       )
                  )



# st.dataframe(df)

# Form


# st.markdown(contact_form, unsafe_allow_html=True)




# Emailer

email_address = {email}
subject = 'New Prospect - Mortgage Calculator - ' + FullName
email_content = f'{email} + {phone}'

fire = firestore.client()

# def send_mail(email_address: str, subject: str, email_content:str):
#     msg = Message(
#         subject=subject,
#         fromaddr=fromaddr,
#         to=email_address,
#         body=email_content
#     )
#
#     mail = Mail(smtpserver, fromaddr, password, smtpport, False, ssl)
#     mail.send(msg)


if st.button('Submit'):
    # st.dataframe(df)
    st.plotly_chart(fig, use_container_width=True)

    # send_mail(email_address, subject, email_content)
    #firebase
    ref.push({
        'contactinfo': {
            'email': f'{email}',
            'etype': 'home',
            'firstname': f'{fname}',
            'lastname': f'{lname}',
            'phonenumber': f'{phone}',
            'ptype': 'mobile'
        }
    })
    #firestore
    doc_ref = fire.collection('prospect').document('contactinfo')
    doc_ref.set({
        'email': f'{email}',
        'etype': 'home',
        'firstname': f'{fname}',
        'lastname': f'{lname}',
        'phonenumber': f'{phone}',
        'ptype': 'mobile'
    })
else:
    st.write('Please complete all fields to continue')

# Use Local CSS File
# def local_css(file_name):
#     with open(file_name) as f:
#         st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
#
#
# local_css("/Users/josephrambow/PycharmProjects/Project-BB/input_form.css")
#

# print(calculations())
