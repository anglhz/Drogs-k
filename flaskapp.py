from flask import Flask, render_template, request, url_for
import pandas as pd
from fuzzywuzzy import fuzz
import smtplib
from email.mime.text import MIMEText
from email.header import Header

app = Flask(__name__)

# Ladda Excel-filen som en DataFrame
excel_path = "/var/www/webserver/drogsok/public_html/static/database/med_list.xlsx"
df = pd.read_excel(excel_path)

# C:/Users/tommy/OneDrive/Skrivbord/drogsok_root/static/database/med_list.xlsx
# /var/www/drogsok_root/static/database/med_list.xlsx


# Definiera en funktion för att söka efter matchningar i första och andra kolumnen
def search_med_list(df, word):
    # Sök efter exakta matchningar i första och andra kolumnen
    matches_col1 = df.loc[df.iloc[:, 0] == word]
    matches_col2 = df.loc[df.iloc[:, 1] == word]
    # Sammanfoga resultaten
    matches = pd.concat([matches_col1, matches_col2]).drop_duplicates()
    # Kontrollera om innehållet i det matchade ordet överensstämmer med något annat ord i kolumnerna
    for index, row in matches.iterrows():
        if word in row[0] or word in row[1]:
            matching_rows = df.loc[
                (df.iloc[:, 0].str.contains(word)) | (df.iloc[:, 1].str.contains(word))
            ]
            matches = pd.concat([matches, matching_rows]).drop_duplicates()
    # Stora bokstäver i den första kolumnen i de matchade raderna
    matches.iloc[:, 0] = matches.iloc[:, 0].str.capitalize()
    # Om ingen exakt match hittades, försök fuzzy matchning
    if matches.empty:
        fuzzy_matches = []
        for index, row in df.iterrows():
            # Beräkna fuzzy matchningspoäng för varje ord i första och andra kolumnen
            score1 = fuzz.token_set_ratio(word, row[0])
            score2 = fuzz.token_set_ratio(word, row[1])
            # Om poängen är större än eller lika med 90, lägg till raden i listan över fuzzy matchningar
            if score1 >= 90 or score2 >= 90:
                fuzzy_matches.append(row)
        # Om det finns några fuzzy matchningar, skapa en dataframe av matchningarna och returnera den
        if fuzzy_matches:
            matches = pd.DataFrame(fuzzy_matches, columns=df.columns).drop_duplicates()
            matches.iloc[:, 0] = matches.iloc[:, 0].str.capitalize()
    return matches

def send_email(subject, body):
    try:
        # Use SMTP_SSL for secure connection
        server = smtplib.SMTP_SSL("cpsrv45.misshosting.com", 465)
        server.login("kontakt@xn--drogsk-0xa.se", "password")  # Replace with the actual password

        # Create a MIMEText object with UTF-8 encoding
        message = MIMEText(body, "plain", "utf-8")
        message["Subject"] = Header(subject, "utf-8")

        # Send the email
        server.sendmail("kontakt@xn--drogsk-0xa.se", "kontakt@xn--drogsk-0xa.se", message.as_string())

        server.quit()
        return True
    except Exception as e:
        print(f"Felmeddelande: {e}")
        return False


def send_email_old(subject, body):
    try:
        #server = smtplib.SMTP("send.one.com", 587)
        server = smtplib.SMTP_SSL("cpsrv45.misshosting.com", 465)
        server.starttls()
        server.login("kontakt@xn--drogsk-0xa.se", "pw")
        message = "From: {}\nTo: {}\nSubject: {}\n\n{}".format(
            "kontakt@xn--drogsk-0xa.se", "kontakt@xn--drogsk-0xa.se", subject, body
        )
        server.sendmail(
            "kontakt@xn--drogsk-0xa.se",
            "kontakt@xn--drogsk-0xa.se",
            message.encode("utf-8"),
        )
        server.quit()
        return True
    except:
        return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    search_term = request.form["search"]
    result = search_med_list(df, search_term.lower())
    return render_template("result.html", result=result, search_term=search_term)


@app.route("/usage")
def usage():
    return render_template("usage.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/mediciner")
def mediciner():
    # UAnvänd panda för att läsa excel filen
    df = pd.read_excel(excel_path)

    # Convertera till html
    content = df.to_html(index=False)

    return content


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/send_email", methods=["POST"])
def send_email_route():
    search_term = request.form["search_term"]
    subject = "Ny Träffrapport"
    body = f"Användaren sökte på: {search_term}"
    email_sent = send_email(
        subject, body
    )  # lägg till parenteser för att anropa funktionen
    if email_sent:
        message = "E-postmeddelandet skickades"
    else:
        message = "E-postmeddelandet kunde inte skickas"
    return message


@app.route("/submit_form", methods=["POST"])
def submit_form():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]

        heading = f"Nytt kontaktformulär: {subject}"
        body = f"Namn: {name}\nEmail: {email}\nÄmne: {subject}\nMeddelande: {message}"

        # Ersätt detta med din e-postadress för mottagaren
        recipient_email = "kontakt@xn--drogsk-0xa.se"

        email_sent = send_email(
            heading, body
        )  # lägg till parenteser för att anropa funktionen
        if email_sent:
            message = "E-postmeddelandet skickades. Vi svarar vanligtvis inom 24 timmar. Tack!"
        else:
            message = "E-postmeddelandet kunde inte skickas. Prova igen eller kontakta administratören kontakt@drogsök.se"
        return message


if __name__ == "__main__":
    app.run()

# if __name__ == "__main__": # Endast för felsökning
#    app.run(host="0.0.0.0", port=5000)
