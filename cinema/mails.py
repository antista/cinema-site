import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

company_email = "galactica.cinema@yandex.ru"
company_email_password = 'Password'


def send_order_info(customer_email, order_code, movie, date, res_sum):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Билеты на киносеанс"
    msg['From'] = company_email
    msg['To'] = customer_email

    text = "Hi!\nThanks for your order\nHere is your tickets code \n{code}".format(code=order_code)
    html = """\
    <html>
      <head></head>
      <body>
        <p>Спасибо за ваш заказ</p>
        <p>Это ваш код для получения билетов. Назовите его контроллеру перед сеансом и оплатите заказ</p>
        <p style="font-weight:bold; font-size:35px">{code}</p>
        <p>Информация о заказе:</p>
        <p>Фильм: {movie}</p>
        <p>Дата сеанса: {date}, время: 20:00</p>
        <p>К оплате: {res_sum} рублей</p>
        <p></p>
        <p>Приятного просмотра!</p>
      </body>
    </html>
    """.format(code=order_code, movie=movie, date=date.strftime("%d %B (%A)"), res_sum=res_sum)

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    s = smtplib.SMTP_SSL('smtp.yandex.com')
    s.login(company_email, company_email_password)
    s.auth_plain()
    s.sendmail(company_email, customer_email, msg.as_string())
    s.quit()
