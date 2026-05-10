import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Configuração Gmail ─────────────────────────────────
GMAIL = "pricelyplus@gmail.com"
GMAIL_PASSWORD = "dbsdfyyehfjgpeuv"

def enviar_alerta(destinatario, produto, preco_antigo, preco_novo, loja):
    """Envia email de alerta quando um preço muda."""
    
    diferenca = preco_novo - preco_antigo
    sinal = "↓ baixou" if diferenca < 0 else "↑ subiu"
    
    assunto = f"Pricely: {produto[:30]} {sinal} em {loja}"
    
    corpo = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        
        <div style="background: #0A3D2B; padding: 24px; text-align: center;">
            <h1 style="color: white; font-size: 28px; margin: 0;">Pricely</h1>
            <p style="color: rgba(255,255,255,0.7); margin: 8px 0 0;">Alerta de preço</p>
        </div>
        
        <div style="padding: 32px; background: #f9f9f9;">
            <h2 style="color: #1a1a1a;">Mudança de preço detectada!</h2>
            
            <div style="background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 24px; margin: 20px 0;">
                <p style="color: #666; margin: 0 0 8px;">Produto</p>
                <p style="font-size: 18px; font-weight: bold; margin: 0;">{produto}</p>
            </div>
            
            <div style="display: flex; gap: 16px; margin: 20px 0;">
                <div style="flex:1; background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; text-align: center;">
                    <p style="color: #666; margin: 0 0 8px;">Preço anterior</p>
                    <p style="font-size: 24px; font-weight: bold; color: #999; margin: 0;">{preco_antigo:.2f} €</p>
                </div>
                <div style="flex:1; background: white; border: 1px solid #0A3D2B; border-radius: 8px; padding: 20px; text-align: center;">
                    <p style="color: #666; margin: 0 0 8px;">Preço actual</p>
                    <p style="font-size: 24px; font-weight: bold; color: #0A3D2B; margin: 0;">{preco_novo:.2f} €</p>
                </div>
            </div>
            
            <div style="background: {'#e8f5e9' if diferenca < 0 else '#fbe9e7'}; border-radius: 8px; padding: 16px; text-align: center; margin: 20px 0;">
                <p style="font-size: 20px; font-weight: bold; color: {'#2e7d32' if diferenca < 0 else '#c62828'}; margin: 0;">
                    {sinal} {abs(diferenca):.2f} € em {loja}
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 32px;">
                <a href="https://v0-pricely-dashboard-design.vercel.app" 
                   style="background: #0A3D2B; color: white; padding: 14px 32px; 
                          text-decoration: none; border-radius: 4px; font-weight: bold;">
                    Ver no Pricely
                </a>
            </div>
        </div>
        
        <div style="padding: 16px; text-align: center; color: #999; font-size: 12px;">
            Pricely · Monitorização de preços automática
        </div>
        
    </body>
    </html>
    """
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = GMAIL
    msg["To"] = destinatario
    msg.attach(MIMEText(corpo, "html"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(GMAIL, GMAIL_PASSWORD)
            servidor.sendmail(GMAIL, destinatario, msg.as_string())
        print(f"✅ Email enviado para {destinatario}!")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False


# ── Teste ──────────────────────────────────────────────
if __name__ == "__main__":
    enviar_alerta(
        destinatario="pricelyplus@gmail.com",
        produto="Apple iPhone 15 128GB Azul",
        preco_antigo=649.00,
        preco_novo=416.00,
        loja="Amazon.es"
    )