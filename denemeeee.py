import smtplib

def mail_send():
    email = "emircancapkan@gmail.com"
    receiver = "salihtekintr@gmail.com"
    password = "ozbymuzyuexjonyl"

    subject = "deneme"
    message = "deneme"
    text = f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    try:
        server.login(email, password)
        server.sendmail(email, receiver, text)
        print("E-mail sent succesfully.")
    except Exception as e:
        print(f"E-mail isn't send. Error: {e}")
    finally:
        server.quit()
