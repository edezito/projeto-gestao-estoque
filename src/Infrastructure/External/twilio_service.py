import os
from twilio.rest import Client

class TwilioService:
    def __init__(self):
        self.sid = os.environ.get("TWILIO_SID")
        self.token = os.environ.get("TWILIO_TOKEN")
        self.from_phone = os.environ.get("TWILIO_PHONE")
        self.client = None
        
        if self.sid and self.token:
            self.client = Client(self.sid, self.token)

    def send_whatsapp_code(self, numero: str, codigo: str) -> bool:
        """Envia o código de ativação via WhatsApp usando Twilio."""
        if not self.client or not self.from_phone:
            print("[AVISO] Twilio não configurado. Pulando envio do WhatsApp.")
            return False

        try:
            self.client.messages.create(
                body=f"Seu código de ativação é: {codigo}",
                from_=f"whatsapp:{self.from_phone}",
                to=f"whatsapp:{numero}",
            )
            return True
        except Exception as e:
            print("Erro ao enviar WhatsApp:", e)
            return False