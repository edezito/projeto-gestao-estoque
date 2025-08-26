from twilio.rest import Client

sid = "SEU_TWILIO_SID"
token = "SEU_TWILIO_TOKEN"
from_phone = "SEU_NUMERO_SANDBOX"  # ex: +14155238886
to_phone = "SEU_NUMERO_CELULAR"   # ex: +5511999999999
codigo = "1234"

client = Client(sid, token)
message = client.messages.create(
    body=f"Seu código de ativação é: {codigo}",
    from_=f"whatsapp:{from_phone}",
    to=f"whatsapp:{to_phone}"
)
print(message.sid)